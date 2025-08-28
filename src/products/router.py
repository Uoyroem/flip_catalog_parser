from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_async_session
from . import schemas, service

_router = APIRouter(prefix="/products")
instance = _router


@_router.post("/parse")
def parse_product():
    return {"detail": "OK"}


@_router.post("/", response_model=schemas.Product, status_code=201)
async def create_product(
    product_in: schemas.ProductCreate,
    async_session: AsyncSession = Depends(get_async_session),
):
    return await service.create_product(
        async_session=async_session, product_in=product_in
    )


@_router.get("/", response_model=list[schemas.Product])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    async_session: AsyncSession = Depends(get_async_session),
):
    products = await service.get_all_products(async_session, skip=skip, limit=limit)
    return products


@_router.get("/{product_id}", response_model=schemas.Product)
async def read_product(
    product_id: int,
    async_session: AsyncSession = Depends(get_async_session),
):
    db_product = await service.get_product(async_session, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@_router.patch("/{product_id}", response_model=schemas.Product)
async def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    async_session: AsyncSession = Depends(get_async_session),
):
    updated_product = await service.update_product(
        async_session, product_id=product_id, product_in=product_in
    )
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@_router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    async_session: AsyncSession = Depends(get_async_session),
):
    deleted_product = await service.delete_product(async_session, product_id=product_id)
    if deleted_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"ok": True}
