from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy import or_

from app.models.category import Category
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.product_variant import ProductVariant, VariantImage
from app.models.order import Order
from app.models.order_items import OrderItem
from app.models.payment import Payment
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.product_variant_repository import ProductVariantRepository
from app.schemas.products import (
    ProductCreate,
    ProductSyncRequest,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantUpdate,
)


class ProductService:
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
        variant_repository: ProductVariantRepository,
    ):
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.variant_repository = variant_repository

    def _get_categories(self, category_ids: list[int]) -> list[Category]:
        categories_by_id = {
            category.id: category
            for category in self.category_repository.get_by_ids(category_ids)
        }
        if len(categories_by_id) != len(category_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more categories were not found.",
            )
        return [categories_by_id[category_id] for category_id in category_ids]

    def create_product(self, product_data: ProductCreate):
        existing = self.product_repository.get_by_external_id(
            product_data.external_id
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A product with this external_id already exists.",
            )

        category_ids = product_data.category_ids or [product_data.category_id]
        categories = self._get_categories(category_ids)

        product = Product(
            external_id=product_data.external_id,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
            image_url=product_data.image_url,
            category_id=categories[0].id,
            categories=categories,
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
                product.categories = [category]
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
                    categories=[category],
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
        category_ids = update_data.pop("category_ids", None)
        if category_ids is None and update_data.get("category_id") is not None:
            category_ids = [update_data["category_id"]]

        if "external_id" in update_data:
            existing = self.product_repository.get_by_external_id(
                update_data["external_id"]
            )

            if existing and existing.id != product.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A product with this external_id already exists.",
                )

        if category_ids is not None:
            categories = self._get_categories(category_ids)
            product.categories = categories
            update_data["category_id"] = categories[0].id

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

    def get_variants(self, product_id: int, active_only: bool = True):
        self.get_product_by_id(product_id)
        return self.variant_repository.get_for_product(product_id, active_only)

    def create_variant(self, product_id: int, variant_data: ProductVariantCreate):
        self.get_product_by_id(product_id)
        if self.variant_repository.get_combination(
            product_id,
            variant_data.color,
            variant_data.length_inches,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This color and length combination already exists.",
            )

        variant = ProductVariant(
            product_id=product_id,
            color=variant_data.color,
            length_inches=variant_data.length_inches,
            price=variant_data.price,
            stock_quantity=variant_data.stock_quantity,
            is_active=True,
            images=[VariantImage(**image.model_dump()) for image in variant_data.images],
        )
        try:
            return self.variant_repository.save(variant)
        except IntegrityError as error:
            self.variant_repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This color and length combination already exists.",
            ) from error

    def update_variant(
        self,
        product_id: int,
        variant_id: int,
        variant_data: ProductVariantUpdate,
    ):
        self.get_product_by_id(product_id)
        variant = self.variant_repository.get_by_id(product_id, variant_id)
        if not variant:
            raise HTTPException(status_code=404, detail="Product variant not found.")

        updates = variant_data.model_dump(exclude_unset=True)
        images = updates.pop("images", None)
        candidate_color = updates.get("color", variant.color)
        candidate_length = updates.get("length_inches", variant.length_inches)
        duplicate = self.variant_repository.get_combination(
            product_id,
            candidate_color,
            candidate_length,
        )
        if duplicate and duplicate.id != variant.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This color and length combination already exists.",
            )

        if images is not None and not images and updates.get("is_active", variant.is_active):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="An active variant must have at least one image.",
            )

        for field, value in updates.items():
            setattr(variant, field, value)
        if images is not None:
            variant.images.clear()
            variant.images.extend(VariantImage(**image.model_dump()) for image in images)
        if updates.get("is_active") is False:
            self.variant_repository.db.query(CartItem).filter(
                CartItem.variant_id == variant.id
            ).delete(synchronize_session=False)
        if variant.is_active and not variant.images:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="An active variant must have at least one image.",
            )

        try:
            self.variant_repository.commit()
            return variant
        except IntegrityError as error:
            self.variant_repository.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This color and length combination already exists.",
            ) from error

    def delete_variant(self, product_id: int, variant_id: int):
        self.get_product_by_id(product_id)
        variant = self.variant_repository.get_by_id(product_id, variant_id)
        if not variant:
            raise HTTPException(status_code=404, detail="Product variant not found.")
        unpaid_order_items = (
            self.variant_repository.db.query(OrderItem.id)
            .join(Order, Order.id == OrderItem.order_id)
            .outerjoin(Payment, Payment.order_id == Order.id)
            .filter(
                OrderItem.variant_id == variant.id,
                or_(Payment.status.is_(None), Payment.status != "successful"),
            )
            .count()
        )
        if unpaid_order_items:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This variant is referenced by an unpaid order. Deactivate it instead.",
            )

        self.variant_repository.db.query(CartItem).filter(
            CartItem.variant_id == variant.id
        ).delete(synchronize_session=False)
        self.variant_repository.db.delete(variant)
        self.variant_repository.commit()
        return {"message": "Product variant deleted. Order snapshots were preserved."}
