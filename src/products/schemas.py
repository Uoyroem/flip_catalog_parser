from decimal import Decimal

from pydantic import ConfigDict

from ..schemas import BaseSchema


class ProductImageBase(BaseSchema):
    url: str
    description: str


class ProductImageCreate(ProductImageBase):
    pass


class ProductImage(ProductImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int


class ProductBase(BaseSchema):
    code: int
    name: str
    description: str | None = None
    price: Decimal
    catalog_id: int


class ProductCreate(ProductBase):
    images: list[ProductImageCreate] = []


class ProductUpdate(ProductBase):
    code: str | None = None
    name: str | None = None
    price: Decimal | None = None
    catalog_id: int | None = None


class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    images: list[ProductImage] = []
