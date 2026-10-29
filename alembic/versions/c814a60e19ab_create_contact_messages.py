"""create contact messages

Revision ID: c814a60e19ab
Revises: 7b5f1a40cd91
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c814a60e19ab"
down_revision: Union[str, Sequence[str], None] = "7b5f1a40cd91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contact_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_contact_messages_id"),
        "contact_messages",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_contact_messages_email"),
        "contact_messages",
        ["email"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_contact_messages_email"), table_name="contact_messages")
    op.drop_index(op.f("ix_contact_messages_id"), table_name="contact_messages")
    op.drop_table("contact_messages")
