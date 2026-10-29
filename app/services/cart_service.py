from fastapi import HTTPException, status

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product_variant import ProductVariant
from app.repositories.cart_repositories import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartItemCreate, CartItemUpdate


class CartService:
    def __init__(
        self,
        cart_repository: CartRepository,
        product_repository: ProductRepository,
    ):
        self.cart_repository = cart_repository
        self.product_repository = product_repository

    def get_or_create_cart(self, guest_session_id: str):
        cart = self.cart_repository.get_cart_by_guest_session_id(guest_session_id)

        if not cart:
            cart = Cart(guest_session_id=guest_session_id)
            cart = self.cart_repository.create_cart(cart)

        return cart

    def add_item(
        self,
        guest_session_id: str,
        item_data: CartItemCreate,
    ):
        cart = self.get_or_create_cart(guest_session_id)

        product = self.product_repository.get_by_id(
            item_data.product_id
        )

        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        variant = None
        if item_data.variant_id is not None:
            variant = (
                self.product_repository.db.query(ProductVariant)
                .filter(
                    ProductVariant.id == item_data.variant_id,
                    ProductVariant.product_id == product.id,
                    ProductVariant.is_active.is_(True),
                )
                .first()
            )
            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product variant is not available.",
                )

        stock_quantity = variant.stock_quantity if variant else product.stock_quantity
        if stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock.",
            )

        existing_item = self.cart_repository.get_cart_item(
            cart.id,
            item_data.product_id,
            item_data.variant_id,
        )

        if existing_item:
            new_quantity = (
                existing_item.quantity + item_data.quantity
            )

            if stock_quantity < new_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient stock.",
                )

            existing_item.quantity = new_quantity

            return self.cart_repository.update_cart_item(
                existing_item
            )

        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            variant_id=item_data.variant_id,
            quantity=item_data.quantity,
        )

        return self.cart_repository.add_cart_item(
            cart_item
        )

    def get_cart(self, guest_session_id: str):
        return self.get_or_create_cart(guest_session_id)

    def update_item(
        self,
        guest_session_id: str,
        cart_item_id: int,
        item_data: CartItemUpdate,
    ):
        cart = self.get_or_create_cart(guest_session_id)

        cart_item = self.cart_repository.get_cart_item_by_id(cart.id, cart_item_id)

        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item was not found.",
            )

        product = self.product_repository.get_by_id(
            cart_item.product_id
        )

        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        variant = cart_item.variant
        stock_quantity = variant.stock_quantity if variant else product.stock_quantity
        if variant and not variant.is_active:
            raise HTTPException(status_code=400, detail="This product variant is no longer available.")

        if stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock.",
            )

        cart_item.quantity = item_data.quantity

        return self.cart_repository.update_cart_item(
            cart_item
        )

    def remove_item(
        self,
        guest_session_id: str,
        cart_item_id: int,
    ):
        cart = self.get_or_create_cart(guest_session_id)

        cart_item = self.cart_repository.get_cart_item_by_id(cart.id, cart_item_id)

        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item was not found.",
            )

        self.cart_repository.delete_cart_item(
            cart_item
        )

        return {
            "message": "Product removed from cart successfully."
        }

    def clear_cart(self, guest_session_id: str):
        cart = self.get_or_create_cart(guest_session_id)

        self.cart_repository.clear_cart(cart)

        return {
            "message": "Cart cleared successfully."
        }