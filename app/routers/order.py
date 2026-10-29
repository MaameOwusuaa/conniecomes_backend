from fastapi import APIRouter, Depends, Header, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.order_repository import OrderRepository
from app.schemas.order import GuestCheckoutCreate, OrderResponse
from app.services.order_service import OrderService


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


def get_order_service(
    db: Session = Depends(get_db),
) -> OrderService:
    repository = OrderRepository(db)

    return OrderService(
        db=db,
        repository=repository,
    )


def get_guest_session_id(
    guest_session_id: str = Header(alias="X-Guest-Session"),
) -> str:
    try:
        return str(UUID(guest_session_id))
    except ValueError as error:
        raise HTTPException(status_code=400, detail="A valid guest session ID is required.") from error


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    checkout: GuestCheckoutCreate,
    guest_session_id: str = Depends(get_guest_session_id),
    service: OrderService = Depends(get_order_service),
):
    try:
        return service.create_guest_order(guest_session_id, checkout)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )