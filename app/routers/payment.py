from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentInitializeResponse
from app.services.payment_service import PaymentService


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def get_payment_service(
    db: Session = Depends(get_db),
) -> PaymentService:
    repository = PaymentRepository(db)

    return PaymentService(
        db=db,
        repository=repository,
    )


@router.post(
    "",
    response_model=PaymentInitializeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payment: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
):
    try:
        return service.create_payment(
            order_id=payment.order_id,
            payment_method=payment.payment_method,
            guest_access_token=payment.guest_access_token,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
"/{payment_id}/verify",
response_model=PaymentResponse,
)
def verify_payment(
    payment_id: int,
    guest_access_token: str = Header(alias="X-Guest-Access-Token"),
    service: PaymentService = Depends(get_payment_service),
):
    try:
        return service.verify_payment(
            payment_id=payment_id,
            guest_access_token=guest_access_token,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )