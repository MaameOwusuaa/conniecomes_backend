from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_items import OrderItem
from app.models.cart import Cart
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.repositories.order_repository import OrderRepository
from app.schemas.order import GuestCheckoutCreate


class OrderService:
    def __init__(
        self,
        db: Session,
        repository: OrderRepository,
    ):
        self.db = db
        self.repository = repository

    def create_guest_order(
        self,
        guest_session_id: str,
        checkout: GuestCheckoutCreate,
    ) -> Order:
        cart = (
            self.db.query(Cart)
            .filter(Cart.guest_session_id == guest_session_id)
            .first()
        )

        if not cart:
            raise ValueError("Cart not found.")

        # Make sure the cart contains products
        if not cart.cart_items:
            raise ValueError("Cannot create an order from an empty cart.")

        total_amount = Decimal("0.00")

        # Create the order first
        order = Order(
            guest_session_id=guest_session_id,
            guest_access_token=str(uuid4()),
            customer_name=checkout.customer_name,
            customer_email=str(checkout.customer_email),
            customer_phone=checkout.customer_phone,
            delivery_address=checkout.delivery_address,
            region=checkout.region,
            delivery_option=checkout.delivery_option,
            total_amount=Decimal("0.00"),
            status="pending",
        )

        self.db.add(order)
        self.db.flush()

        # Create order items
        for cart_item in cart.cart_items:

            product = (
                self.db.query(Product)
                .filter(Product.id == cart_item.product_id)
                .first()
            )

            if not product or not product.is_active:
                raise ValueError(
                    f"Product {cart_item.product_id} not found."
                )

            variant = cart_item.variant
            if variant and (
                not variant.is_active
                or variant.product_id != product.id
            ):
                raise ValueError(f"The selected variant for {product.name} is unavailable.")

            if cart_item.quantity <= 0:
                raise ValueError(
                    f"Invalid quantity for product {product.id}."
                )

            stock_quantity = variant.stock_quantity if variant else product.stock_quantity
            if stock_quantity < cart_item.quantity:
                raise ValueError(
                    f"Not enough stock for {product.name}"
                    f"{' (' + variant.color + ', ' + str(variant.length_inches) + ' inches)' if variant else ''}."
                )

            unit_price = Decimal(str(variant.price or product.price)) if variant else Decimal(str(product.price))

            item_total = unit_price * cart_item.quantity

            total_amount += item_total

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                variant_id=variant.id if variant else None,
                variant_color=variant.color if variant else None,
                variant_length_inches=variant.length_inches if variant else None,
                quantity=cart_item.quantity,
                unit_price=unit_price,
            )

            self.db.add(order_item)

        # Update the order total
        order.total_amount = total_amount

        self.db.commit()
        self.db.refresh(order)

        return order

    def get_order(
        self,
        order_id: int,
        user_id: int,
    ) -> Order:

        order = self.repository.get_by_id(order_id)

        if not order:
            raise ValueError("Order not found.")

        if order.user_id != user_id:
            raise ValueError("You do not have access to this order.")

        return order

    def get_user_orders(
        self,
        user_id: int,
    ) -> list[Order]:

        return self.repository.get_by_user_id(user_id)