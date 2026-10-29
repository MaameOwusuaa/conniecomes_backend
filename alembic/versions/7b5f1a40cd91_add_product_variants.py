"""add product variants and order snapshots

Revision ID: 7b5f1a40cd91
Revises: 4df875cf15a2
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b5f1a40cd91"
down_revision: Union[str, Sequence[str], None] = "4df875cf15a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("color", sa.String(length=80), nullable=False),
        sa.Column("length_inches", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("stock_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "color", "length_inches", name="uq_product_variant_combination"),
    )
    op.create_index("ix_product_variants_id", "product_variants", ["id"])
    op.create_index("ix_product_variants_product_id", "product_variants", ["product_id"])

    op.create_table(
        "variant_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("variant_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_variant_images_id", "variant_images", ["id"])
    op.create_index("ix_variant_images_variant_id", "variant_images", ["variant_id"])

    op.add_column("cart_items", sa.Column("variant_id", sa.Integer(), nullable=True))
    op.create_index("ix_cart_items_variant_id", "cart_items", ["variant_id"])
    op.create_foreign_key(
        "fk_cart_items_variant_id_product_variants",
        "cart_items",
        "product_variants",
        ["variant_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("order_items", sa.Column("variant_id", sa.Integer(), nullable=True))
    op.add_column("order_items", sa.Column("variant_color", sa.String(length=80), nullable=True))
    op.add_column("order_items", sa.Column("variant_length_inches", sa.Integer(), nullable=True))
    op.create_index("ix_order_items_variant_id", "order_items", ["variant_id"])
    op.create_foreign_key(
        "fk_order_items_variant_id_product_variants",
        "order_items",
        "product_variants",
        ["variant_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_order_items_variant_id_product_variants", "order_items", type_="foreignkey")
    op.drop_index("ix_order_items_variant_id", table_name="order_items")
    op.drop_column("order_items", "variant_length_inches")
    op.drop_column("order_items", "variant_color")
    op.drop_column("order_items", "variant_id")
    op.drop_constraint("fk_cart_items_variant_id_product_variants", "cart_items", type_="foreignkey")
    op.drop_index("ix_cart_items_variant_id", table_name="cart_items")
    op.drop_column("cart_items", "variant_id")
    op.drop_index("ix_variant_images_variant_id", table_name="variant_images")
    op.drop_index("ix_variant_images_id", table_name="variant_images")
    op.drop_table("variant_images")
    op.drop_index("ix_product_variants_product_id", table_name="product_variants")
    op.drop_index("ix_product_variants_id", table_name="product_variants")
    op.drop_table("product_variants")