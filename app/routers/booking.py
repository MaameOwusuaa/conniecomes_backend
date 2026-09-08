from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
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
    current_user: User = Depends(
        get_current_user
    ),
    service: BookingService = Depends(
        get_booking_service
    ),
):

    try:

        return service.create_booking(
            user_id=current_user.id,
            service=booking.service,
            booking_date=booking.booking_date,
            notes=booking.notes,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# ============================================================
# GET CURRENT USER'S BOOKINGS
# ============================================================

@router.get(
    "",
    response_model=list[BookingResponse],
)
def get_user_bookings(
    current_user: User = Depends(
        get_current_user
    ),
    service: BookingService = Depends(
        get_booking_service
    ),
):

    return service.get_user_bookings(
        current_user.id
    )


# ============================================================
# GET ONE BOOKING
# ============================================================

@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def get_booking(
    booking_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    service: BookingService = Depends(
        get_booking_service
    ),
):

    try:

        return service.get_booking(
            booking_id,
            current_user.id,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ============================================================
# UPDATE BOOKING
# ============================================================

@router.put(
    "/{booking_id}",
    response_model=BookingResponse,
)
def update_booking(
    booking_id: int,
    booking: BookingUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    service: BookingService = Depends(
        get_booking_service
    ),
):

    try:

        return service.update_booking(
            booking_id=booking_id,
            user_id=current_user.id,
            service=booking.service,
            booking_date=booking.booking_date,
            notes=booking.notes,
            status=booking.status,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# ============================================================
# DELETE BOOKING
# ============================================================

@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_booking(
    booking_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    service: BookingService = Depends(
        get_booking_service
    ),
):

    try:

        service.delete_booking(
            booking_id,
            current_user.id,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )