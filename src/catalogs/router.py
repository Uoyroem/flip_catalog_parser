from fastapi import APIRouter, Depends, HTTPException
from selenium.webdriver import Chrome
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_async_session, get_driver
from . import schemas, service

_router = APIRouter(prefix="/catalogs")
instance = _router


@_router.post("/", response_model=schemas.Catalog, status_code=201)
async def create_catalog(
    catalog_in: schemas.CatalogCreate,
    async_session: AsyncSession = Depends(get_async_session),
):
    return await service.create_catalog(
        async_session=async_session, catalog_in=catalog_in
    )


@_router.get("/", response_model=list[schemas.Catalog])
async def read_catalogs(
    skip: int = 0,
    limit: int = 100,
    async_session: AsyncSession = Depends(get_async_session),
):
    catalogs = await service.get_all_catalogs(async_session, skip=skip, limit=limit)
    return catalogs


@_router.get("/{catalog_id}", response_model=schemas.Catalog)
async def read_catalog(
    catalog_id: int,
    async_session: AsyncSession = Depends(get_async_session),
):
    db_catalog = await service.get_catalog_by_id(async_session, id=catalog_id)
    if db_catalog is None:
        raise HTTPException(status_code=404, detail="Catalog not found")
    return db_catalog


@_router.patch("/{catalog_id}", response_model=schemas.Catalog)
async def update_catalog(
    catalog_id: int,
    catalog_in: schemas.CatalogUpdate,
    async_session: AsyncSession = Depends(get_async_session),
):
    updated_catalog = await service.update_catalog_by_id(
        async_session, id=catalog_id, catalog_in=catalog_in
    )
    if updated_catalog is None:
        raise HTTPException(status_code=404, detail="Catalog not found")
    return updated_catalog


@_router.delete("/{catalog_id}", status_code=204)
async def delete_catalog(
    catalog_id: int,
    async_session: AsyncSession = Depends(get_async_session),
):
    deleted_catalog = await service.delete_catalog_by_id(async_session, id=catalog_id)
    if deleted_catalog is None:
        raise HTTPException(status_code=404, detail="Catalog not found")
    return {"ok": True}


# @_router.post("/parse/by-url")
# async def parse_catalog_by_url(
#     catalog_id: int,
#     async_session: AsyncSession = Depends(get_async_session),
#     driver: Chrome = Depends(get_driver)
# ):
#     pass


@_router.post("/{catalog_id}/parse-products")
async def parse_catalog_products_by_id(
    catalog_id: int,
    page: int = 1,
    limit: int = 10,
    async_session: AsyncSession = Depends(get_async_session),
    driver: Chrome = Depends(get_driver),
):
    await service.upsert_parsed_catalog_products_by_id(
        async_session=async_session,
        driver=driver,
        page=page,
        limit=limit,
        id=catalog_id,
    )

    return {"ok": True}


@_router.post("/parse-products/by-code/{code}")
async def parse_catalog_products_by_code(
    code: int,
    page: int = 1,
    limit: int = 10,
    async_session: AsyncSession = Depends(get_async_session),
    driver: Chrome = Depends(get_driver),
):
    await service.upsert_parsed_catalog_products_by_code(
        async_session=async_session,
        driver=driver,
        page=page,
        limit=limit,
        code=code,
    )

    return {"ok": True}


@_router.post("/parse-products/by-url")
async def parse_catalog_products_by_url(
    url: str,
    page: int = 1,
    limit: int = 10,
    async_session: AsyncSession = Depends(get_async_session),
    driver: Chrome = Depends(get_driver),
):
    await service.upsert_parsed_catalog_products_by_url(
        async_session=async_session,
        driver=driver,
        page=page,
        limit=limit,
        url=url,
    )

    return {"ok": True}
