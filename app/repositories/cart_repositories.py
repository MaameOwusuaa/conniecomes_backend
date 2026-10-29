from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_cart_by_guest_session_id(self, guest_session_id: str):
        return (
            self.db.query(Cart)
            .filter(Cart.guest_session_id == guest_session_id)
            .first()
        )

    def create_cart(self, cart: Cart):
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def get_cart_item(
        self,
        cart_id: int,
        product_id: int,
        variant_id: int | None = None,
    ):
        query = self.db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )
        if variant_id is None:
            query = query.filter(CartItem.variant_id.is_(None))
        else:
            query = query.filter(CartItem.variant_id == variant_id)
        return query.first()

    def get_cart_item_by_id(self, cart_id: int, cart_item_id: int):
        return (
            self.db.query(CartItem)
            .filter(CartItem.cart_id == cart_id, CartItem.id == cart_item_id)
            .first()
        )

    def add_cart_item(self, cart_item: CartItem):
        self.db.add(cart_item)
        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item

    def update_cart_item(self, cart_item: CartItem):
        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item

    def delete_cart_item(self, cart_item: CartItem):
        self.db.delete(cart_item)
        self.db.commit()

    def clear_cart(self, cart: Cart):
        self.db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).delete()

        self.db.commit()

        self.db.refresh(cart)

        return cart