from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from . import models, schemas


async def parse_product(code: int):
    pass



async def get_product(async_session: AsyncSession, product_id: int):
    result = await async_session.execute(
        select(models.Product)
        .options(selectinload(models.Product.images))
        .where(models.Product.id == product_id)
    )
    return result.scalars().first()


async def get_all_products(
    async_session: AsyncSession, skip: int = 0, limit: int = 100
):
    result = await async_session.execute(
        select(models.Product)
        .options(selectinload(models.Product.images))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def create_product(
    async_session: AsyncSession, product_in: schemas.ProductCreate
):
    product_data = product_in.model_dump(exclude={"images"})
    db_product = models.Product(**product_data)

    if product_in.images:
        for image_in in product_in.images:
            db_image = models.ProductImage(**image_in.model_dump())
            db_product.images.append(db_image)

    async_session.add(db_product)
    await async_session.commit()
    await async_session.refresh(db_product)
    return db_product


async def update_product(
    self,
    async_session: AsyncSession,
    product_id: int,
    product_in: schemas.ProductUpdate,
):
    db_product = await self.get_product(async_session, product_id)
    if not db_product:
        return None
    update_data = product_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    async_session.add(db_product)
    await async_session.commit()
    await async_session.refresh(db_product)
    return db_product


async def delete_product(async_session: AsyncSession, product_id: int):
    db_product = await get_product(async_session, product_id)
    if not db_product:
        return None
    await async_session.delete(db_product)
    await async_session.commit()
    return db_product
