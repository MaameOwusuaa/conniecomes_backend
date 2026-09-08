from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookingCreate(BaseModel):
    service: str = Field(min_length=2, max_length=150)
    booking_date: datetime
    notes: str | None = None


class BookingUpdate(BaseModel):
    service: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    booking_date: datetime | None = None

    notes: str | None = None

    status: str | None = None


class BookingResponse(BaseModel):
    id: int
    user_id: int
    service: str
    booking_date: datetime
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )