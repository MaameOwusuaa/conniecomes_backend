from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_admin_user
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


def get_category_service(db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    return CategoryService(repository)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=201,
)
def create_category(
    category: CategoryCreate,
    _admin=Depends(get_admin_user),
    service: CategoryService = Depends(get_category_service),
):
    return service.create_category(category)


@router.get(
    "",
    response_model=list[CategoryResponse],
)
def get_categories(
    service: CategoryService = Depends(get_category_service),
):
    return service.get_all_categories()


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
):
    return service.get_category_by_id(category_id)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    _admin=Depends(get_admin_user),
    service: CategoryService = Depends(get_category_service),
):
    return service.update_category(
        category_id,
        category,
    )


@router.delete(
    "/{category_id}",
)
def delete_category(
    category_id: int,
    _admin=Depends(get_admin_user),
    service: CategoryService = Depends(get_category_service),
):
    return service.delete_category(category_id)