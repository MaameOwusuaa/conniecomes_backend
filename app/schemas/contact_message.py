from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ContactMessageCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    message: str = Field(min_length=1, max_length=5000)

    @field_validator("name", "message", mode="before")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("This field cannot be blank.")
        return value


class ContactMessageResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
