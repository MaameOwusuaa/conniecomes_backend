import base64
import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import get_admin_user
from app.core.config import settings
from app.models.booking import Booking
from app.models.contact_message import ContactMessage
from app.models.order import Order
from app.models.order_items import OrderItem
from app.models.payment import Payment
from app.models.product import Product
from app.models.user import User
from app.services.booking_notification_service import BookingNotificationService


router = APIRouter(prefix="/admin", tags=["Administration"])


class BookingStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|confirmed|completed|cancelled)$")


class OrderDeliveryStatusUpdate(BaseModel):
    delivery_status: str = Field(
        pattern="^(pending|preparing|out_for_delivery|delivered|delivery_failed)$"
    )


class ImageUploadRequest(BaseModel):
    data_url: str = Field(max_length=7_000_000)


@router.get("/customers")
def list_customers(
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    all_orders = db.query(Order).options(joinedload(Order.payment)).order_by(Order.created_at.desc()).all()
    all_bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()
    registered_users = (
        db.query(User)
        .options(selectinload(User.orders).joinedload(Order.payment), selectinload(User.bookings))
        .filter(User.is_admin.is_(False))
        .all()
    )

    aggregates: dict[str, dict] = {}

    def guest_key(email: str | None = None, phone: str | None = None, name: str | None = None, session_id: str | None = None) -> str | None:
        if email and email.strip():
            value = email.strip().lower().encode("utf-8")
            return "guest:email:" + base64.urlsafe_b64encode(value).decode("ascii")
        if phone and phone.strip():
            value = phone.strip().encode("utf-8")
            return "guest:phone:" + base64.urlsafe_b64encode(value).decode("ascii")
        if name and name.strip():
            value = name.strip().lower().encode("utf-8")
            return "guest:name:" + base64.urlsafe_b64encode(value).decode("ascii")
        if session_id and session_id.strip():
            value = session_id.strip().encode("utf-8")
            return "guest:session:" + base64.urlsafe_b64encode(value).decode("ascii")
        return None

    def add_guest(email: str | None, phone: str | None, name: str | None, session_id: str | None, record_type: str, record) -> None:
        key = guest_key(email, phone, name, session_id)
        if not key:
            return
        customer = aggregates.setdefault(key, {
            "id": key,
            "first_name": (name or "Guest").strip().split()[0] if name else "Guest",
            "last_name": " ".join((name or "").strip().split()[1:]) if name else "Customer",
            "email": email or "No email provided",
            "is_active": True,
            "email_verified": False,
            "is_guest": True,
            "created_at": record.created_at.isoformat(),
            "orders": [],
            "bookings": [],
        })
        if record_type == "order":
            customer["orders"].append(record)
        else:
            customer["bookings"].append(record)

    for customer in registered_users:
        key = f"user:{customer.id}"
        aggregates[key] = {
            "id": key,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "is_active": customer.is_active,
            "email_verified": customer.email_verified,
            "is_guest": False,
            "created_at": customer.created_at.isoformat(),
            "orders": list(customer.orders),
            "bookings": list(customer.bookings),
        }

    for order in all_orders:
        if order.user_id:
            continue
        add_guest(order.customer_email, order.customer_phone, order.customer_name, order.guest_session_id, "order", order)

    for booking in all_bookings:
        if booking.user_id:
            continue
        add_guest(booking.customer_email, booking.customer_phone, booking.customer_name, None, "booking", booking)

    return [
        {
            "id": customer["id"],
            "first_name": customer["first_name"],
            "last_name": customer["last_name"],
            "email": customer["email"],
            "is_active": customer["is_active"],
            "email_verified": customer["email_verified"],
            "is_guest": customer["is_guest"],
            "created_at": customer["created_at"],
            "order_count": len(customer["orders"]),
            "booking_count": len(customer["bookings"]),
            "paid_sales": float(sum(
                (order.total_amount for order in customer["orders"] if order.payment and order.payment.status == "successful"),
                Decimal("0.00"),
            )),
            "open_order_count": sum(
                1 for order in customer["orders"]
                if order.payment is None or order.payment.status != "successful" or order.delivery_status != "delivered"
            ),
        }
        for customer in aggregates.values()
    ]


@router.get("/customers/{customer_id}")
def get_customer_details(
    customer_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    if customer_id.startswith("user:"):
        user_id = int(customer_id.removeprefix("user:"))
        customer = (
            db.query(User)
            .options(
                selectinload(User.orders).joinedload(Order.payment),
                selectinload(User.orders).selectinload(Order.order_items),
                selectinload(User.bookings),
            )
            .filter(User.id == user_id, User.is_admin.is_(False))
            .first()
        )
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found.")
        customer_id_response = customer_id
        first_name = customer.first_name
        last_name = customer.last_name
        email = customer.email
        is_active = customer.is_active
        email_verified = customer.email_verified
        is_guest = False
        created_at = customer.created_at
        updated_at = customer.updated_at
        orders = list(customer.orders)
        bookings = list(customer.bookings)
    elif customer_id.startswith("guest:"):
        parts = customer_id.split(":", 2)
        if len(parts) != 3:
            raise HTTPException(status_code=404, detail="Customer not found.")
        _, guest_type, encoded_value = parts
        try:
            value = base64.urlsafe_b64decode(encoded_value.encode("ascii")).decode("utf-8")
        except Exception as error:
            raise HTTPException(status_code=404, detail="Customer not found.") from error

        order_query = db.query(Order).options(joinedload(Order.payment), joinedload(Order.order_items)).filter(Order.user_id.is_(None))
        booking_query = db.query(Booking).filter(Booking.user_id.is_(None))
        if guest_type == "email":
            order_query = order_query.filter(Order.customer_email.ilike(value))
            booking_query = booking_query.filter(Booking.customer_email.ilike(value))
        elif guest_type == "phone":
            order_query = order_query.filter(Order.customer_phone == value)
            booking_query = booking_query.filter(Booking.customer_phone == value)
        elif guest_type == "name":
            order_query = order_query.filter(Order.customer_name.ilike(value))
            booking_query = booking_query.filter(Booking.customer_name.ilike(value))
        elif guest_type == "session":
            order_query = order_query.filter(Order.guest_session_id == value)
        else:
            raise HTTPException(status_code=404, detail="Customer not found.")

        orders = order_query.all()
        bookings = booking_query.all()
        if not orders and not bookings:
            raise HTTPException(status_code=404, detail="Customer not found.")
        name_source = next((order.customer_name for order in orders if order.customer_name), None) or next((booking.customer_name for booking in bookings if booking.customer_name), None)
        name_parts = (name_source or "Guest Customer").strip().split()
        first_name = name_parts[0] if name_parts else "Guest"
        last_name = " ".join(name_parts[1:]) or "Customer"
        email = next((order.customer_email for order in orders if order.customer_email), None) or next((booking.customer_email for booking in bookings if booking.customer_email), None) or "No email provided"
        is_active = True
        email_verified = False
        is_guest = True
        customer_id_response = customer_id
        created_records = [*orders, *bookings]
        created_at = max(created_records, key=lambda record: record.created_at).created_at if created_records else datetime.now()
        updated_at = created_at
    else:
        raise HTTPException(status_code=404, detail="Customer not found.")

    product_ids = {item.product_id for order in orders for item in order.order_items}
    products = {
        product.id: product
        for product in db.query(Product).filter(Product.id.in_(product_ids)).all()
    } if product_ids else {}

    orders = sorted(orders, key=lambda order: order.created_at, reverse=True)
    bookings = sorted(
        bookings,
        key=lambda booking: (booking.booking_date, booking.booking_time),
        reverse=True,
    )
    return {
        "id": customer_id_response,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "is_active": is_active,
        "email_verified": email_verified,
        "is_guest": is_guest,
        "created_at": created_at.isoformat(),
        "updated_at": updated_at.isoformat(),
        "orders": [
            {
                "id": order.id,
                "created_at": order.created_at.isoformat(),
                "total_amount": float(order.total_amount),
                "status": order.status,
                "payment_status": order.payment.status if order.payment else "unpaid",
                "payment": {
                    "id": order.payment.id,
                    "amount": float(order.payment.amount),
                    "method": order.payment.payment_method,
                    "status": order.payment.status,
                    "reference": order.payment.transaction_reference,
                    "created_at": order.payment.created_at.isoformat(),
                } if order.payment else None,
                "delivery_status": order.delivery_status,
                "phone": order.customer_phone,
                "delivery_address": order.delivery_address,
                "delivery_region": order.region,
                "delivery_option": order.delivery_option,
                "items": [
                    {
                        "product_name": products[item.product_id].name if item.product_id in products else "Removed product",
                        "variant_color": item.variant_color,
                        "variant_length_inches": item.variant_length_inches,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                        "line_total": float(item.unit_price * item.quantity),
                    }
                    for item in order.order_items
                ],
            }
            for order in orders
        ],
        "bookings": [
            {
                "id": booking.id,
                "service": booking.service,
                "booking_date": booking.booking_date.isoformat(),
                "booking_time": booking.booking_time.isoformat(),
                "status": booking.status,
                "notes": booking.notes,
                "phone": booking.customer_phone,
            }
            for booking in bookings
        ],
    }


@router.delete("/transactions/cleared")
def clear_transaction_history(
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    successful_orders = (
        db.query(Order)
        .join(Payment, Payment.order_id == Order.id)
        .options(joinedload(Order.payment), joinedload(Order.order_items))
        .filter(Payment.status == "successful")
        .all()
    )
    if not successful_orders:
        return {"deleted_orders": 0, "deleted_payments": 0, "deleted_order_items": 0}

    deleted_orders = 0
    deleted_payments = 0
    deleted_order_items = 0
    try:
        for order in successful_orders:
            if order.payment:
                db.delete(order.payment)
                deleted_payments += 1
            deleted_order_items += len(order.order_items)
            for item in list(order.order_items):
                db.delete(item)
            db.delete(order)
            deleted_orders += 1
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Transaction history could not be cleared because another database record depends on these orders.",
        ) from error

    return {
        "deleted_orders": deleted_orders,
        "deleted_payments": deleted_payments,
        "deleted_order_items": deleted_order_items,
    }


@router.get("/orders")
def list_all_orders(
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    orders = (
        db.query(Order)
        .options(
            joinedload(Order.user),
            joinedload(Order.payment),
            joinedload(Order.order_items),
        )
        .order_by(Order.created_at.desc())
        .all()
    )
    product_ids = {item.product_id for order in orders for item in order.order_items}
    products = {
        product.id: product
        for product in db.query(Product).filter(Product.id.in_(product_ids)).all()
    } if product_ids else {}

    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "buyer_name": order.customer_name or (
                f"{order.user.first_name} {order.user.last_name}" if order.user else "Legacy customer"
            ),
            "buyer_email": order.customer_email or (order.user.email if order.user else ""),
            "buyer_phone": order.customer_phone,
            "delivery_address": order.delivery_address,
            "delivery_region": order.region,
            "delivery_option": order.delivery_option,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "payment_status": order.payment.status if order.payment else "unpaid",
            "delivery_status": order.delivery_status,
            "created_at": order.created_at.isoformat(),
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": products[item.product_id].name if item.product_id in products else "Removed product",
                    "variant_color": item.variant_color,
                    "variant_length_inches": item.variant_length_inches,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "line_total": float(item.unit_price * item.quantity),
                }
                for item in order.order_items
            ],
        }
        for order in orders
    ]


@router.get("/bookings")
def list_all_bookings(
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.user))
        .order_by(Booking.booking_date.desc(), Booking.booking_time.desc())
        .all()
    )

    return [
        {
            "id": booking.id,
            "user_id": booking.user_id,
            "customer_name": booking.customer_name or (
                f"{booking.user.first_name} {booking.user.last_name}" if booking.user else "Customer"
            ),
            "customer_email": booking.customer_email or (booking.user.email if booking.user else ""),
            "service": booking.service,
            "booking_date": booking.booking_date.isoformat(),
            "booking_time": booking.booking_time.isoformat(),
            "notes": booking.notes,
            "status": booking.status,
            "created_at": booking.created_at.isoformat(),
        }
        for booking in bookings
    ]


@router.get("/contact-messages")
def list_contact_messages(
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    return (
        db.query(ContactMessage)
        .order_by(ContactMessage.created_at.desc())
        .all()
    )


@router.patch("/bookings/{booking_id}")
def update_booking_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    if booking.status == payload.status:
        return {
            "id": booking.id,
            "status": booking.status,
            "notifications": None,
        }

    booking.status = payload.status
    db.commit()
    db.refresh(booking)

    notifications = BookingNotificationService().send_status_update(booking)
    return {
        "id": booking.id,
        "status": booking.status,
        "notifications": notifications,
    }


@router.patch("/orders/{order_id}/delivery-status")
def update_order_delivery_status(
    order_id: int,
    payload: OrderDeliveryStatusUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    order.delivery_status = payload.delivery_status
    db.commit()
    db.refresh(order)
    return {"id": order.id, "delivery_status": order.delivery_status}


@router.get("/analytics")
def get_sales_analytics(
    period: str = Query("monthly", pattern="^(daily|weekly|monthly|quarterly|yearly)$"),
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    today = date.today()

    def month_start(month_offset: int) -> date:
        month_index = today.year * 12 + today.month - 1 + month_offset
        return date(month_index // 12, month_index % 12 + 1, 1)

    if period == "daily":
        bucket_starts = [today - timedelta(days=offset) for offset in reversed(range(14))]
    elif period == "weekly":
        current_week = today - timedelta(days=today.weekday())
        bucket_starts = [current_week - timedelta(weeks=offset) for offset in reversed(range(12))]
    elif period == "monthly":
        bucket_starts = [month_start(-offset) for offset in reversed(range(12))]
    elif period == "quarterly":
        current_quarter = date(today.year, ((today.month - 1) // 3) * 3 + 1, 1)
        bucket_starts = []
        for offset in reversed(range(8)):
            month_index = current_quarter.year * 12 + current_quarter.month - 1 - offset * 3
            bucket_starts.append(date(month_index // 12, month_index % 12 + 1, 1))
    else:
        bucket_starts = [date(today.year - offset, 1, 1) for offset in reversed(range(5))]

    first_start = bucket_starts[0]
    payments = (
        db.query(Payment.created_at, Payment.amount)
        .filter(
            Payment.status == "successful",
            Payment.created_at >= datetime.combine(first_start, time.min),
        )
        .all()
    )

    def bucket_key(payment_date: date) -> str:
        if period == "daily":
            return payment_date.isoformat()
        if period == "weekly":
            iso = payment_date.isocalendar()
            return f"{iso.year}-W{iso.week:02d}"
        if period == "monthly":
            return payment_date.strftime("%Y-%m")
        if period == "quarterly":
            return f"{payment_date.year}-Q{(payment_date.month - 1) // 3 + 1}"
        return str(payment_date.year)

    def start_key(start: date) -> str:
        return bucket_key(start)

    amounts = {start_key(start): Decimal("0.00") for start in bucket_starts}
    for created_at, amount in payments:
        key = bucket_key(created_at.date())
        if key in amounts:
            amounts[key] += Decimal(str(amount))

    chart = []
    for start in bucket_starts:
        key = start_key(start)
        if period == "daily":
            label = start.strftime("%b %d")
        elif period == "weekly":
            label = f"Week of {start.strftime('%b %d')}"
        elif period == "monthly":
            label = start.strftime("%b %Y")
        elif period == "quarterly":
            label = f"Q{(start.month - 1) // 3 + 1} {start.year}"
        else:
            label = str(start.year)
        chart.append({"label": label, "amount": float(amounts[key])})

    revenue = sum(amounts.values(), Decimal("0.00"))
    order_count = (
        db.query(Payment.id)
        .filter(
            Payment.status == "successful",
            Payment.created_at >= datetime.combine(first_start, time.min),
        )
        .count()
    )
    return {
        "period": period,
        "total_revenue": float(revenue),
        "successful_orders": order_count,
        "chart": chart,
    }


@router.post("/uploads", status_code=status.HTTP_201_CREATED)
def upload_image(
    payload: ImageUploadRequest,
    _admin=Depends(get_admin_user),
):
    match = re.fullmatch(
        r"data:image/(jpeg|png|webp|gif);base64,([A-Za-z0-9+/=\s]+)",
        payload.data_url,
    )
    if not match:
        raise HTTPException(status_code=400, detail="Upload a PNG, JPEG, WEBP, or GIF image.")

    encoded = re.sub(r"\s+", "", match.group(2))
    try:
        content = base64.b64decode(encoded, validate=True)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="The image data is invalid.") from error

    if not content or len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Images must be smaller than 5 MB.")

    extension = "jpg" if match.group(1) == "jpeg" else match.group(1)
    filename = f"{uuid4().hex}.{extension}"
    upload_dir = settings.UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / filename).write_bytes(content)
    return {"image_url": f"/uploads/{filename}"}
