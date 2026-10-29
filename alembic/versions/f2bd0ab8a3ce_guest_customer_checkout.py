"""support guest checkout and bookings

Revision ID: f2bd0ab8a3ce
Revises: e51a7c93d204
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2bd0ab8a3ce"
down_revision: Union[str, Sequence[str], None] = "e51a7c93d204"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("carts", "user_id", existing_type=sa.Integer(), nullable=True)
    op.add_column("carts", sa.Column("guest_session_id", sa.String(length=36), nullable=True))
    op.create_index("ix_carts_guest_session_id", "carts", ["guest_session_id"], unique=True)

    op.alter_column("orders", "user_id", existing_type=sa.Integer(), nullable=True)
    op.add_column("orders", sa.Column("guest_session_id", sa.String(length=36), nullable=True))
    op.add_column("orders", sa.Column("guest_access_token", sa.String(length=36), nullable=True))
    op.add_column("orders", sa.Column("customer_name", sa.String(length=255), nullable=True))
    op.add_column("orders", sa.Column("customer_email", sa.String(length=255), nullable=True))
    op.add_column("orders", sa.Column("customer_phone", sa.String(length=50), nullable=True))
    op.add_column("orders", sa.Column("delivery_address", sa.Text(), nullable=True))
    op.add_column("orders", sa.Column("region", sa.String(length=100), nullable=True))
    op.add_column("orders", sa.Column("delivery_option", sa.String(length=50), nullable=True))
    op.create_index("ix_orders_guest_access_token", "orders", ["guest_access_token"], unique=True)

    op.alter_column("bookings", "user_id", existing_type=sa.Integer(), nullable=True)
    op.add_column("bookings", sa.Column("customer_name", sa.String(length=255), nullable=True))
    op.add_column("bookings", sa.Column("customer_email", sa.String(length=255), nullable=True))
    op.add_column("bookings", sa.Column("customer_phone", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("bookings", "customer_phone")
    op.drop_column("bookings", "customer_email")
    op.drop_column("bookings", "customer_name")
    op.alter_column("bookings", "user_id", existing_type=sa.Integer(), nullable=False)

    op.drop_index("ix_orders_guest_access_token", table_name="orders")
    op.drop_column("orders", "delivery_option")
    op.drop_column("orders", "region")
    op.drop_column("orders", "delivery_address")
    op.drop_column("orders", "customer_phone")
    op.drop_column("orders", "customer_email")
    op.drop_column("orders", "customer_name")
    op.drop_column("orders", "guest_access_token")
    op.drop_column("orders", "guest_session_id")
    op.alter_column("orders", "user_id", existing_type=sa.Integer(), nullable=False)

    op.drop_index("ix_carts_guest_session_id", table_name="carts")
    op.drop_column("carts", "guest_session_id")
    op.alter_column("carts", "user_id", existing_type=sa.Integer(), nullable=False)
