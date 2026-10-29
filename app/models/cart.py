from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Cart(BaseModel):
    __tablename__ = "carts"

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        unique=True,
    )

    guest_session_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        unique=True,
        index=True,
    )

    user = relationship(
        "User",
        back_populates="cart",
    )

    cart_items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
    )