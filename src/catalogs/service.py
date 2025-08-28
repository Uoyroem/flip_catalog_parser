from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import selenium.webdriver
import undetected_chromedriver
from . import models, schemas


async def parse_catalog_products(
    driver: selenium.webdriver.Chrome,
    async_session: AsyncSession,
    catalog_id: int,
    page: int,
    limit: int,
):
    catalog = await get_catalog(async_session, catalog_id)
    if catalog is None:
        return False
    driver.get(f"https://www.flip.kz/catalog?subsection={catalog.code}")

    

async def get_catalog(async_session: AsyncSession, catalog_id: int):
    result = await async_session.execute(
        select(models.Catalog).where(models.Catalog.id == catalog_id)
    )
    return result.scalars().first()


async def get_all_catalogs(
    async_session: AsyncSession, skip: int = 0, limit: int = 100
):
    result = await async_session.execute(
        select(models.Catalog).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_catalog(
    async_session: AsyncSession, catalog_in: schemas.CatalogCreate
):
    db_catalog = models.Catalog(**catalog_in.model_dump())
    async_session.add(db_catalog)
    await async_session.commit()
    await async_session.refresh(db_catalog)
    return db_catalog


async def update_catalog(
    async_session: AsyncSession,
    catalog_id: int,
    catalog_in: schemas.CatalogUpdate,
):
    db_catalog = await get_catalog(async_session, catalog_id)
    if not db_catalog:
        return None
    update_data = catalog_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_catalog, key, value)
    async_session.add(db_catalog)
    await async_session.commit()
    return await get_catalog(async_session, catalog_id)


async def delete_catalog(async_session: AsyncSession, catalog_id: int):
    db_catalog = await get_catalog(async_session, catalog_id)
    if not db_catalog:
        return None
    await async_session.delete(db_catalog)
    await async_session.commit()
    return db_catalog
