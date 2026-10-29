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
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        service: str,
        booking_date,
        booking_time,
        notes: str | None = None,
    ) -> Booking:

        return self.repository.create(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            service=service,
            booking_date=booking_date,
            booking_time=booking_time,
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
        booking_time=None,
        notes=None,
    ) -> Booking:

        booking = self.get_booking(
            booking_id,
            user_id,
        )

        if service is not None:
            booking.service = service

        if booking_date is not None:
            booking.booking_date = booking_date

        if booking_time is not None:
            booking.booking_time = booking_time

        if notes is not None:
            booking.notes = notes

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