from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_admin_user
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.product_variant_repository import ProductVariantRepository
from app.schemas.products import (
    ProductCreate,
    ProductResponse,
    ProductSyncRequest,
    ProductSyncResponse,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


def get_product_service(db: Session = Depends(get_db)):
    product_repository = ProductRepository(db)
    category_repository = CategoryRepository(db)
    variant_repository = ProductVariantRepository(db)

    return ProductService(
        product_repository,
        category_repository,
        variant_repository,
    )


@router.post(
    "/sync",
    response_model=ProductSyncResponse,
    status_code=200,
)
def sync_frontend_catalog(
    request: ProductSyncRequest,
    _admin=Depends(get_admin_user),
    service: ProductService = Depends(get_product_service),
):
    return service.sync_frontend_catalog(request)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=201,
)
def create_product(
    product: ProductCreate,
    _admin=Depends(get_admin_user),
    service: ProductService = Depends(get_product_service),
):
    return service.create_product(product)


@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_products(
    service: ProductService = Depends(get_product_service),
):
    return service.get_all_products()


@router.get(
    "/external/{external_id}",
    response_model=ProductResponse,
)
def get_product_by_external_id(
    external_id: str,
    service: ProductService = Depends(get_product_service),
):
    return service.get_product_by_external_id(external_id)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    return service.get_product_by_id(product_id)


@router.get(
    "/{product_id}/variants",
    response_model=list[ProductVariantResponse],
)
def get_product_variants(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    return service.get_variants(product_id)


@router.get(
    "/{product_id}/variants/manage",
    response_model=list[ProductVariantResponse],
)
def get_product_variants_for_admin(
    product_id: int,
    _admin=Depends(get_admin_user),
    service: ProductService = Depends(get_product_service),
):
    return service.get_variants(product_id, active_only=False)


@router.post(
    "/{product_id}/variants",
    response_model=ProductVariantResponse,
    status_code=201,
)
def create_product_variant(
    product_id: int,
    variant: ProductVariantCreate,
    _admin=Depends(get_admin_user),
    service: ProductService = Depends(get_product_service),
):
    return service.create_variant(product_id, variant)


@router.put(
    "/{product_id}/variants/{variant_id}",
    response_model=ProductVariantResponse,
)
def update_product_variant(
    product_id: int,
    variant_id: int,
    variant: ProductVariantUpdate,
    _admin=Depends(get_admin_user),
    service: ProductService = Depends(get_product_service),
):
    return service.update_variant(product_id, variant_id, variant)


@router.delete(
    "/{product_id}/variants/{variant_id}",
)
def deactivate_product_variant(
    product_id: int,
    variant_id: int,
    _admin=Depends(get_admin_user),
    service: ProductService = Depends(get_product_service),
):
    return service.delete_variant(product_id, variant_id)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    product: ProductUpdate,
    _admin=Depends(get_admin_user),
    service: ProductService = Depends(get_product_service),
):
    return service.update_product(
        product_id,
        product,
    )


@router.delete(
    "/{product_id}",
)
def delete_product(
    product_id: int,
    _admin=Depends(get_admin_user),
    service: ProductService = Depends(get_product_service),
):
    return service.delete_product(product_id)
