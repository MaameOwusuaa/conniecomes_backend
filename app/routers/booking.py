from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingUpdate,
)
from app.services.booking_service import BookingService


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


def get_booking_service(
    db: Session = Depends(get_db),
) -> BookingService:

    repository = BookingRepository(db)

    return BookingService(
        repository=repository
    )


# ============================================================
# CREATE BOOKING
# ============================================================

@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    booking: BookingCreate,
    service: BookingService = Depends(
        get_booking_service
    ),
):

    try:

        return service.create_booking(
            customer_name=booking.customer_name,
            customer_email=str(booking.customer_email),
            customer_phone=booking.customer_phone,
            service=booking.service,
            booking_date=booking.booking_date,
            booking_time=booking.booking_time,
            notes=booking.notes,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
