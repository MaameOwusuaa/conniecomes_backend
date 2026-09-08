from app.models.booking import Booking
from app.repositories.booking_repository import BookingRepository


class BookingService:

    def __init__(
        self,
        repository: BookingRepository,
    ):
        self.repository = repository

    def create_booking(
        self,
        user_id: int,
        service: str,
        booking_date,
        notes: str | None = None,
    ) -> Booking:

        return self.repository.create(
            user_id=user_id,
            service=service,
            booking_date=booking_date,
            notes=notes,
        )

    def get_user_bookings(
        self,
        user_id: int,
    ) -> list[Booking]:

        return self.repository.get_by_user(user_id)

    def get_booking(
        self,
        booking_id: int,
        user_id: int,
    ) -> Booking:

        booking = self.repository.get_by_id(
            booking_id,
            user_id,
        )

        if not booking:
            raise ValueError(
                "Booking not found."
            )

        return booking

    def update_booking(
        self,
        booking_id: int,
        user_id: int,
        service=None,
        booking_date=None,
        notes=None,
        status=None,
    ) -> Booking:

        booking = self.get_booking(
            booking_id,
            user_id,
        )

        if service is not None:
            booking.service = service

        if booking_date is not None:
            booking.booking_date = booking_date

        if notes is not None:
            booking.notes = notes

        if status is not None:
            booking.status = status

        return self.repository.update(
            booking
        )

    def delete_booking(
        self,
        booking_id: int,
        user_id: int,
    ) -> None:

        booking = self.get_booking(
            booking_id,
            user_id,
        )

        self.repository.delete(
            booking
        )