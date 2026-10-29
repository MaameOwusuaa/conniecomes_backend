from sqlalchemy.orm import Session

from app.models.booking import Booking


class BookingRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        service: str,
        booking_date,
        booking_time,
        notes: str | None = None,
    ) -> Booking:

        booking = Booking(
            user_id=None,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            service=service,
            booking_date=booking_date,
            booking_time=booking_time,
            notes=notes,
            status="pending",
        )

        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)

        return booking

    def get_by_id(
        self,
        booking_id: int,
        user_id: int,
    ) -> Booking | None:

        return (
            self.db.query(Booking)
            .filter(
                Booking.id == booking_id,
                Booking.user_id == user_id,
            )
            .first()
        )

    def get_by_user(
        self,
        user_id: int,
    ) -> list[Booking]:

        return (
            self.db.query(Booking)
            .filter(
                Booking.user_id == user_id
            )
            .order_by(
                Booking.booking_date.desc()
            )
            .all()
        )

    def update(
        self,
        booking: Booking,
    ) -> Booking:

        self.db.commit()
        self.db.refresh(booking)

        return booking

    def delete(
        self,
        booking: Booking,
    ) -> None:

        self.db.delete(booking)
        self.db.commit()