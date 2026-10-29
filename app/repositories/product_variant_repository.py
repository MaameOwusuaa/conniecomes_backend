from sqlalchemy.orm import Session, selectinload

from app.models.product_variant import ProductVariant


class ProductVariantRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_for_product(self, product_id: int, active_only: bool = True):
        query = (
            self.db.query(ProductVariant)
            .options(selectinload(ProductVariant.images))
            .filter(ProductVariant.product_id == product_id)
        )
        if active_only:
            query = query.filter(ProductVariant.is_active.is_(True))
        return query.order_by(ProductVariant.length_inches, ProductVariant.color).all()

    def get_by_id(self, product_id: int, variant_id: int):
        return (
            self.db.query(ProductVariant)
            .options(selectinload(ProductVariant.images))
            .filter(
                ProductVariant.product_id == product_id,
                ProductVariant.id == variant_id,
            )
            .first()
        )

    def get_combination(self, product_id: int, color: str, length_inches: int):
        return (
            self.db.query(ProductVariant)
            .filter(
                ProductVariant.product_id == product_id,
                ProductVariant.color.ilike(color),
                ProductVariant.length_inches == length_inches,
            )
            .first()
        )

    def save(self, variant: ProductVariant) -> ProductVariant:
        self.db.add(variant)
        self.db.commit()
        self.db.refresh(variant)
        return variant

    def commit(self) -> None:
        self.db.commit()