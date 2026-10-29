from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict
from pydantic import EmailStr, Field


class GuestCheckoutCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=255)
    customer_email: EmailStr
    customer_phone: str = Field(min_length=6, max_length=50)
    delivery_address: str = Field(min_length=5, max_length=1000)
    region: str = Field(min_length=2, max_length=100)
    delivery_option: str = Field(pattern="^(standard|express|pickup)$")


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str | None = None
    variant_id: int | None = None
    variant_color: str | None = None
    variant_length_inches: int | None = None
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int | None = None
    guest_access_token: str | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None
    delivery_address: str | None = None
    region: str | None = None
    delivery_option: str | None = None
    total_amount: Decimal
    status: str
    order_items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)