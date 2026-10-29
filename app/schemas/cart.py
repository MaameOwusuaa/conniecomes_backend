from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.products import ProductVariantResponse


class CartItemCreate(BaseModel):
    product_id: int
    variant_id: int | None = None
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: Decimal
    stock_quantity: int
    image_url: str

    model_config = ConfigDict(
        from_attributes=True
    )


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    variant_id: int | None
    quantity: int
    product: CartProductResponse
    variant: ProductVariantResponse | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class CartResponse(BaseModel):
    id: int
    user_id: int | None = None
    cart_items: list[CartItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )