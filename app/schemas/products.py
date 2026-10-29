from datetime import datetime
from decimal import Decimal

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VariantImageInput(BaseModel):
    image_url: str = Field(min_length=1, max_length=500)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, value: str) -> str:
        value = value.strip()
        if not value or re.search(r"\s", value):
            raise ValueError("Image URL must be a valid URL or local path.")
        if not value.startswith(("http://", "https://", "/", "../", "./")):
            raise ValueError("Image URL must be absolute or a site-relative path.")
        return value


def validate_variant_length(value: int) -> int:
    if value < 8 or value > 32 or value % 2:
        raise ValueError("Variant lengths must be even values from 8 to 32 inches.")
    return value


class ProductVariantCreate(BaseModel):
    color: str = Field(min_length=2, max_length=80)
    length_inches: int = Field(ge=8, le=32)
    price: Decimal | None = Field(default=None, gt=0)
    stock_quantity: int = Field(ge=0)
    images: list[VariantImageInput] = Field(min_length=1, max_length=10)

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        value = " ".join(value.split())
        if not re.fullmatch(r"[\w][\w .'-]{0,79}", value):
            raise ValueError("Color contains unsupported characters.")
        return value

    @field_validator("length_inches")
    @classmethod
    def validate_length(cls, value: int) -> int:
        return validate_variant_length(value)


class ProductVariantUpdate(BaseModel):
    color: str | None = Field(default=None, min_length=2, max_length=80)
    length_inches: int | None = Field(default=None, ge=8, le=32)
    price: Decimal | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    images: list[VariantImageInput] | None = Field(default=None, max_length=10)

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Color cannot be null.")
        value = " ".join(value.split())
        if not re.fullmatch(r"[\w][\w .'-]{0,79}", value):
            raise ValueError("Color contains unsupported characters.")
        return value

    @field_validator("length_inches")
    @classmethod
    def validate_length(cls, value: int | None) -> int | None:
        if value is None:
            raise ValueError("Length cannot be null.")
        return validate_variant_length(value)

    @field_validator("stock_quantity", "is_active")
    @classmethod
    def validate_required_variant_fields(cls, value):
        if value is None:
            raise ValueError("This variant field cannot be null.")
        return value


class VariantImageResponse(VariantImageInput):
    id: int
    variant_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductVariantResponse(BaseModel):
    id: int
    product_id: int
    color: str
    length_inches: int
    price: Decimal | None
    stock_quantity: int
    is_active: bool
    images: list[VariantImageResponse]

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: Decimal = Field(gt=0)
    stock_quantity: int = Field(ge=0)
    length_inches: int | None = Field(default=None, ge=1, le=100)
    image_url: str | None = None
    category_id: int
    category_ids: list[int] | None = Field(default=None, min_length=1)

    @field_validator("category_ids")
    @classmethod
    def validate_unique_category_ids(cls, value: list[int] | None) -> list[int] | None:
        if value is not None and len(value) != len(set(value)):
            raise ValueError("Category IDs must be unique.")
        return value


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
    length_inches: int | None = Field(default=None, ge=1, le=100)
    image_url: str | None = None
    category_id: int | None = None
    category_ids: list[int] | None = Field(default=None, min_length=1)
    is_active: bool | None = None

    @field_validator("category_id")
    @classmethod
    def validate_category_id(cls, value: int | None) -> int | None:
        if value is None:
            raise ValueError("Category ID cannot be null.")
        return value

    @field_validator("category_ids")
    @classmethod
    def validate_unique_category_ids(cls, value: list[int] | None) -> list[int] | None:
        if value is not None and len(value) != len(set(value)):
            raise ValueError("Category IDs must be unique.")
        return value


class ProductResponse(ProductBase):
    id: int
    external_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: "CategoryResponse | None" = None
    categories: list["CategoryResponse"] = Field(default_factory=list)
    variants: list[ProductVariantResponse] = Field(default_factory=list)

    model_config = ConfigDict(
        from_attributes=True
    )

    @field_validator("variants", mode="before")
    @classmethod
    def active_variants_only(cls, value):
        if value is None:
            return []
        return [variant for variant in value if variant.is_active]


from app.schemas.category import CategoryResponse

ProductResponse.model_rebuild()


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
