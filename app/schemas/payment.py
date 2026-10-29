from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    guest_access_token: str


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    payment_method: str
    status: str
    transaction_reference: str | None
    authorization_url: str | None = None
    access_code: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaymentInitializeResponse(BaseModel):
    payment: PaymentResponse
    authorization_url: str
    access_code: str