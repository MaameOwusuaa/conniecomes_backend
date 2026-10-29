from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookingCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=255)
    customer_email: EmailStr
    customer_phone: str = Field(min_length=6, max_length=50)
    service: str = Field(min_length=2, max_length=150)
    booking_date: date
    booking_time: time
    notes: str | None = None


class BookingUpdate(BaseModel):
    service: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    booking_date: date | None = None

    booking_time: time | None = None

    notes: str | None = None

class BookingResponse(BaseModel):
    id: int
    user_id: int | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None
    service: str
    booking_date: date
    booking_time: time
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )