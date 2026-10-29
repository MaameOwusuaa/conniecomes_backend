from fastapi import HTTPException, status

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def create_category(self, category_data: CategoryCreate):
        existing_category = self.repository.get_by_name(category_data.name)

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exists.",
            )

        category = Category(
            name=category_data.name,
            description=category_data.description,
        )

        return self.repository.create(category)

    def get_all_categories(self):
        return self.repository.get_all()

    def get_category_by_id(self, category_id: int):
        category = self.repository.get_by_id(category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        return category

    def update_category(
        self,
        category_id: int,
        category_data: CategoryUpdate,
    ):
        category = self.get_category_by_id(category_id)

        if category_data.name is not None:
            existing = self.repository.get_by_name(category_data.name)

            if existing and existing.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category already exists.",
                )

            category.name = category_data.name

        if category_data.description is not None:
            category.description = category_data.description

        self.repository.update()

        return category

    def delete_category(self, category_id: int):
        category = self.get_category_by_id(category_id)

        for product in list(category.products):
            remaining_categories = [
                assigned_category
                for assigned_category in product.categories
                if assigned_category.id != category.id
            ]
            if not remaining_categories:
                self.repository.db.delete(product)
                continue

            product.categories = remaining_categories
            if product.category_id == category.id:
                product.category_id = remaining_categories[0].id

        self.repository.delete(category)

        return {
            "message": "Category deleted successfully."
        }