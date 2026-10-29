from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.cart_repositories import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import (
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartResponse,
)
from app.services.cart_service import CartService


router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


def get_cart_service(
    db: Session = Depends(get_db),
):
    cart_repository = CartRepository(db)
    product_repository = ProductRepository(db)

    return CartService(
        cart_repository,
        product_repository,
    )


def get_guest_session_id(
    guest_session_id: str = Header(alias="X-Guest-Session"),
) -> str:
    try:
        return str(UUID(guest_session_id))
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid guest session ID is required.",
        ) from error


@router.get(
    "",
    response_model=CartResponse,
)
def get_cart(
    guest_session_id: str = Depends(get_guest_session_id),
    service: CartService = Depends(get_cart_service),
):
    return service.get_cart(guest_session_id)


@router.post(
    "/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_item_to_cart(
    item: CartItemCreate,
    guest_session_id: str = Depends(get_guest_session_id),
    service: CartService = Depends(get_cart_service),
):
    return service.add_item(
        guest_session_id,
        item,
    )


@router.put(
    "/items/{cart_item_id}",
    response_model=CartItemResponse,
)
def update_cart_item(
    cart_item_id: int,
    item: CartItemUpdate,
    guest_session_id: str = Depends(get_guest_session_id),
    service: CartService = Depends(get_cart_service),
):
    return service.update_item(
        guest_session_id,
        cart_item_id,
        item,
    )


@router.delete(
    "/items/{cart_item_id}",
)
def remove_cart_item(
    cart_item_id: int,
    guest_session_id: str = Depends(get_guest_session_id),
    service: CartService = Depends(get_cart_service),
):
    return service.remove_item(
        guest_session_id,
        cart_item_id,
    )


@router.delete(
    "",
)
def clear_cart(
    guest_session_id: str = Depends(get_guest_session_id),
    service: CartService = Depends(get_cart_service),
):
    return service.clear_cart(guest_session_id)