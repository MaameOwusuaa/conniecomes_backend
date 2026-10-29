"""rename wigs category to custom made wig caps

Revision ID: e51a7c93d204
Revises: b753c1de91af
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e51a7c93d204"
down_revision: Union[str, Sequence[str], None] = "b753c1de91af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    categories = sa.table(
        "categories",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )
    existing = connection.execute(
        sa.select(categories.c.id, categories.c.name).where(
            categories.c.name.in_(["Wigs", "Custom Made Wig Caps"])
        )
    ).all()
    category_ids = {name: category_id for category_id, name in existing}
    old_id = category_ids.get("Wigs")

    if old_id is None:
        return

    new_id = category_ids.get("Custom Made Wig Caps")
    if new_id is None:
        op.execute(
            sa.update(categories)
            .where(categories.c.id == old_id)
            .values(
                name="Custom Made Wig Caps",
                description="Custom made wig caps and wigs.",
            )
        )
        return

    op.execute(
        sa.text(
            "INSERT INTO product_categories (product_id, category_id) "
            "SELECT old_links.product_id, :new_id "
            "FROM product_categories AS old_links "
            "WHERE old_links.category_id = :old_id "
            "AND NOT EXISTS ("
            "SELECT 1 FROM product_categories AS new_links "
            "WHERE new_links.product_id = old_links.product_id "
            "AND new_links.category_id = :new_id"
            ")"
        ).bindparams(old_id=old_id, new_id=new_id)
    )
    op.execute(
        sa.update(
            sa.table(
                "products",
                sa.column("category_id", sa.Integer),
            )
        )
        .where(sa.column("category_id", sa.Integer) == old_id)
        .values(category_id=new_id)
    )
    op.execute(sa.delete(categories).where(categories.c.id == old_id))
    op.execute(
        sa.update(categories)
        .where(categories.c.id == new_id)
        .values(description="Custom made wig caps and wigs.")
    )


def downgrade() -> None:
    connection = op.get_bind()
    categories = sa.table(
        "categories",
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )
    op.execute(
        sa.update(categories)
        .where(categories.c.name == "Custom Made Wig Caps")
        .values(
            name="Wigs",
            description="Ready-made wigs and wig caps.",
        )
    )
