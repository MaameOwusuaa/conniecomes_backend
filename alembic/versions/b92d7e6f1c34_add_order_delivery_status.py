"""Add order delivery tracking status.

Revision ID: b92d7e6f1c34
Revises: f2bd0ab8a3ce
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b92d7e6f1c34"
down_revision: Union[str, Sequence[str], None] = "f2bd0ab8a3ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column(
            "delivery_status",
            sa.String(length=50),
            server_default="pending",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("orders", "delivery_status")
