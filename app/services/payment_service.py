from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.order import Order
from app.models.payment import Payment
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.repositories.payment_repository import PaymentRepository
from app.services.paystack_service import PaystackService


class PaymentService:
    def __init__(
        self,
        db: Session,
        repository: PaymentRepository,
    ):
        self.db = db
        self.repository = repository
        self.paystack = PaystackService()

    def create_payment(
        self,
        order_id: int,
        payment_method: str,
        guest_access_token: str,
    ) -> Payment:

        # Find the order
        order = (
            self.db.query(Order)
            .filter(
                Order.id == order_id,
                Order.guest_access_token == guest_access_token,
            )
            .first()
        )

        if not order:
            raise ValueError("Order not found.")

        # Only pending orders can be paid
        if order.status != "pending":
            raise ValueError(
                "This order cannot be paid."
            )

        # Check whether a payment already exists
        existing_payment = (
            self.repository.get_by_order_id(order_id)
        )

        if existing_payment:
            raise ValueError(
                "A payment already exists for this order."
            )

        # Validate payment method
        allowed_methods = {
            "card",
            "mobile_money",
        }

        if payment_method not in allowed_methods:
            raise ValueError(
                "Invalid payment method. "
                "Use 'card' or 'mobile_money'."
            )

        # Get amount directly from the order
        amount = Decimal(str(order.total_amount))

        # Generate a temporary transaction reference
        transaction_reference = (
            f"TXN-{uuid4().hex[:12].upper()}"
        )

        payment = Payment(
            order_id=order.id,
            amount=amount,
            payment_method=payment_method,
            status="pending",
            transaction_reference=transaction_reference,
        )

        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        # Convert GHS to pesewas
        amount_in_pesewas = int(amount * 100)

        # Initialize transaction with Paystack
        paystack_data = self.paystack.initialize_transaction(
            email=order.customer_email,
            amount=amount_in_pesewas,
            reference=transaction_reference,
        )

        return {
            "payment": payment,
            "authorization_url": paystack_data["authorization_url"],
            "access_code": paystack_data["access_code"],
        }

    def verify_payment(
        self,
        payment_id: int,
        guest_access_token: str,
    ) -> Payment:

        # Find the payment
        payment = self.repository.get_by_id(payment_id)

        if not payment:
            raise ValueError("Payment not found.")

        # Find the related order
        order = (
            self.db.query(Order)
            .filter(Order.id == payment.order_id)
            .first()
        )

        if not order:
            raise ValueError("Order not found.")

        if order.guest_access_token != guest_access_token:
            raise ValueError(
                "Invalid guest order access token."
            )

        # Prevent duplicate payment
        if payment.status == "successful":
            raise ValueError(
                "This payment has already been completed."
            )

        if order.status == "paid":
            raise ValueError(
                "This order has already been paid."
            )

        # Find the guest's cart
        cart = (
            self.db.query(Cart)
            .filter(Cart.guest_session_id == order.guest_session_id)
            .first()
        )

        if not cart:
            raise ValueError("Cart not found.")

        # Verify the transaction with Paystack
        paystack_data = self.paystack.verify_transaction(
            payment.transaction_reference
        )

        # Make sure Paystack confirms the payment was successful
        if paystack_data.get("status") != "success":
            raise ValueError(
                "Payment has not been completed."
            )

        # Verify the amount paid
        paystack_amount = (
            Decimal(str(paystack_data["amount"]))
            / Decimal("100")
        )

        if paystack_amount != payment.amount:
            raise ValueError(
                "Payment amount does not match "
                "the order amount."
            )

        inventory_totals = {}
        for order_item in order.order_items:
            key = (
                ("variant", order_item.variant_id)
                if order_item.variant_id
                else ("product", order_item.product_id)
            )
            inventory_totals[key] = inventory_totals.get(key, 0) + order_item.quantity

        inventory_to_decrement = []
        for (inventory_type, inventory_id), quantity in inventory_totals.items():
            if inventory_type == "variant":
                variant = (
                    self.db.query(ProductVariant)
                    .filter(ProductVariant.id == inventory_id)
                    .with_for_update()
                    .first()
                )
                if not variant:
                    raise ValueError("The selected product variant is no longer available.")
                if variant.stock_quantity < quantity:
                    raise ValueError(
                        f"Not enough stock for {variant.product.name}"
                        f" ({variant.color}, {variant.length_inches} inches)."
                    )
                inventory_to_decrement.append((variant, quantity))
            else:
                product = (
                    self.db.query(Product)
                    .filter(Product.id == inventory_id)
                    .with_for_update()
                    .first()
                )
                if not product:
                    raise ValueError(f"Product {inventory_id} not found.")
                if product.stock_quantity < quantity:
                    raise ValueError(f"Not enough stock for {product.name if product else 'product'}.")
                inventory_to_decrement.append((product, quantity))

        for inventory_item, quantity in inventory_to_decrement:
            inventory_item.stock_quantity -= quantity

        # Mark payment as successful
        payment.status = "successful"

        # Mark order as paid
        order.status = "paid"

        # Clear the cart
        for cart_item in list(cart.cart_items):
            self.db.delete(cart_item)

        # Save all changes
        self.db.commit()

        # Refresh payment from database
        self.db.refresh(payment)

        return payment