from pydantic import ConfigDict

from ..schemas import BaseSchema


class CatalogBase(BaseSchema):
    code: int
    name: str
    parent_id: int | None = None


class CatalogCreate(CatalogBase):
    pass


class CatalogUpdate(CatalogBase):
    code: str | None = None
    name: str | None = None


class Catalog(CatalogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
