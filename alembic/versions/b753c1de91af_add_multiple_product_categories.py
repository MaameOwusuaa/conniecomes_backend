"""support multiple categories per product

Revision ID: b753c1de91af
Revises: c814a60e19ab
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b753c1de91af"
down_revision: Union[str, Sequence[str], None] = "c814a60e19ab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_categories",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("product_id", "category_id"),
    )
    op.create_index(
        "ix_product_categories_category_id",
        "product_categories",
        ["category_id"],
    )
    op.execute(
        sa.text(
            "INSERT INTO product_categories (product_id, category_id) "
            "SELECT id, category_id FROM products"
        )
    )


def downgrade() -> None:
    op.drop_index(
        "ix_product_categories_category_id",
        table_name="product_categories",
    )
    op.drop_table("product_categories")
