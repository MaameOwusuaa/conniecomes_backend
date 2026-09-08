from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_all(self):
        return self.db.query(Product).all()

    def get_active(self):
        return (
            self.db.query(Product)
            .filter(Product.is_active.is_(True))
            .all()
        )

    def get_by_id(self, product_id: int):
        return (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

    def get_by_external_id(self, external_id: str):
        return (
            self.db.query(Product)
            .filter(Product.external_id == external_id)
            .first()
        )

    def update(self):
        self.db.commit()

    def delete(self, product: Product):
        self.db.delete(product)
        self.db.commit()
