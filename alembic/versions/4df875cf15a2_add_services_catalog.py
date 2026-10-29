"""add services catalog

Revision ID: 4df875cf15a2
Revises: 98bada8ef628
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4df875cf15a2"
down_revision: Union[str, Sequence[str], None] = "98bada8ef628"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


services_table = sa.table(
    "services",
    sa.column("name", sa.String),
    sa.column("description", sa.Text),
    sa.column("image_url", sa.String),
    sa.column("is_active", sa.Boolean),
)
categories_table = sa.table(
    "categories",
    sa.column("name", sa.String),
    sa.column("description", sa.String),
)


def upgrade() -> None:
    op.add_column("products", sa.Column("length_inches", sa.Integer(), nullable=True))
    connection = op.get_bind()
    existing_categories = set(connection.execute(sa.select(categories_table.c.name)).scalars())
    starter_categories = [
        {"name": "Custom Made Wig Caps", "description": "Custom made wig caps and wigs."},
        {"name": "Frontals", "description": "Hair frontals and lace pieces."},
        {"name": "Closures", "description": "Hair closures and lace pieces."},
        {"name": "Bundles", "description": "Premium hair bundles."},
    ]
    missing_categories = [
        category for category in starter_categories
        if category["name"] not in existing_categories
    ]
    if missing_categories:
        op.bulk_insert(categories_table, missing_categories)
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.bulk_insert(
        services_table,
        [
            {"name": "Hair Braiding", "description": "Professional Conniecomes service.", "image_url": "../images/Braids.png", "is_active": True},
            {"name": "Frontal Installation", "description": "Professional Conniecomes service.", "image_url": "../images/Frontal_installation.png", "is_active": True},
            {"name": "Custom Wig Making", "description": "Professional Conniecomes service.", "image_url": "../images/custom made wigs.jpg", "is_active": True},
            {"name": "Manicure", "description": "Professional Conniecomes service.", "image_url": "../images/Manicure.png", "is_active": True},
            {"name": "Pedicure", "description": "Professional Conniecomes service.", "image_url": "../images/Pedicure.png", "is_active": True},
        ],
    )


def downgrade() -> None:
    op.drop_table("services")
    op.drop_column("products", "length_inches")