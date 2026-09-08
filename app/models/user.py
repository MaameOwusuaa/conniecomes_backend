from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)

    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    """
    orders: Mapped[list["Order"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan",
)
    
    cart: Mapped["Cart"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    """
    
    cart = relationship(
    "Cart",
    back_populates="user",
    uselist=False,
)

    orders = relationship(
        "Order",
        back_populates="user",
    )

    bookings = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
    )