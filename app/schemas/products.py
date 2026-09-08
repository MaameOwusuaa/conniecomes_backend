from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: Decimal = Field(gt=0)
    stock_quantity: int = Field(ge=0)
    image_url: str | None = None
    category_id: int


class ProductCreate(ProductBase):
    external_id: str = Field(min_length=1, max_length=100)


class ProductUpdate(BaseModel):
    external_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    name: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    image_url: str | None = None
    category_id: int | None = None
    is_active: bool | None = None


class ProductResponse(ProductBase):
    id: int
    external_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ProductSyncItem(BaseModel):
    """
    Product data read from the frontend catalog.

    The frontend owns the catalog definition.
    The database stores the synchronized copy used by
    carts, orders, payments, and inventory.
    """

    external_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(gt=0)
    stock_quantity: int = Field(ge=0)
    category: str = Field(min_length=1, max_length=100)
    category_description: str | None = None
    image_url: str | None = None


class ProductSyncRequest(BaseModel):
    products: list[ProductSyncItem] = Field(min_length=1)


class ProductSyncResponse(BaseModel):
    created: int
    updated: int
    products: list[ProductResponse]
