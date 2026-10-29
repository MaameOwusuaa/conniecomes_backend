from sqlalchemy import Column, ForeignKey, Index, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


product_categories = Table(
    "product_categories",
    BaseModel.metadata,
    Column(
        "product_id",
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
Index("ix_product_categories_category_id", product_categories.c.category_id)


class Category(BaseModel):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    products = relationship(
        "Product",
        secondary=product_categories,
        back_populates="categories",
        passive_deletes=True,
    )