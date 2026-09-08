from fastapi import HTTPException, status

from app.models.category import Category
from app.models.product import Product
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.products import (
    ProductCreate,
    ProductSyncRequest,
    ProductUpdate,
)


class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
    ):
        self.product_repository = product_repository
        self.category_repository = category_repository

    def create_product(self, product_data: ProductCreate):
        existing = self.product_repository.get_by_external_id(
            product_data.external_id
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A product with this external_id already exists.",
            )

        category = self.category_repository.get_by_id(
            product_data.category_id
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        product = Product(
            external_id=product_data.external_id,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
            image_url=product_data.image_url,
            category_id=product_data.category_id,
            is_active=True,
        )

        return self.product_repository.create(product)

    def sync_frontend_catalog(self, request: ProductSyncRequest):
        """
        Synchronize the catalog defined by the frontend into MySQL.

        Categories are created automatically when they do not exist.
        Products are matched by external_id, never by the MySQL id.
        """

        created = 0
        updated = 0
        synced_products = []
        seen_external_ids = set()

        for item in request.products:
            external_id = item.external_id.strip()

            if external_id in seen_external_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Duplicate external_id in frontend catalog: "
                        f"{external_id}"
                    ),
                )

            seen_external_ids.add(external_id)

            category_name = item.category.strip()
            category = self.category_repository.get_by_name(
                category_name
            )

            if not category:
                category = Category(
                    name=category_name,
                    description=item.category_description,
                )
                self.product_repository.db.add(category)
                self.product_repository.db.flush()

            elif (
                item.category_description is not None
                and category.description != item.category_description
            ):
                category.description = item.category_description

            product = self.product_repository.get_by_external_id(
                external_id
            )

            if product:
                product.name = item.name
                product.description = item.description
                product.price = item.price
                product.image_url = item.image_url
                product.category_id = category.id
                product.is_active = True
                updated += 1
            else:
                product = Product(
                    external_id=external_id,
                    name=item.name,
                    description=item.description,
                    price=item.price,
                    stock_quantity=item.stock_quantity,
                    image_url=item.image_url,
                    category_id=category.id,
                    is_active=True,
                )
                self.product_repository.db.add(product)
                created += 1

            synced_products.append(product)

        self.product_repository.db.commit()

        for product in synced_products:
            self.product_repository.db.refresh(product)

        return {
            "created": created,
            "updated": updated,
            "products": synced_products,
        }

    def get_all_products(self):
        return self.product_repository.get_active()

    def get_product_by_id(self, product_id: int):
        product = self.product_repository.get_by_id(product_id)

        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        return product

    def get_product_by_external_id(self, external_id: str):
        product = self.product_repository.get_by_external_id(
            external_id
        )

        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        return product

    def update_product(
        self,
        product_id: int,
        product_data: ProductUpdate,
    ):
        product = self.get_product_by_id(product_id)

        update_data = product_data.model_dump(exclude_unset=True)

        if "external_id" in update_data:
            existing = self.product_repository.get_by_external_id(
                update_data["external_id"]
            )

            if existing and existing.id != product.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A product with this external_id already exists.",
                )

        if (
            "category_id" in update_data
            and update_data["category_id"] is not None
        ):
            category = self.category_repository.get_by_id(
                update_data["category_id"]
            )

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found.",
                )

        for field, value in update_data.items():
            setattr(product, field, value)

        self.product_repository.update()

        return product

    def delete_product(self, product_id: int):
        product = self.get_product_by_id(product_id)

        # Soft-delete so old carts/orders retain their product relationship.
        product.is_active = False
        self.product_repository.update()

        return {
            "message": "Product deactivated successfully."
        }
