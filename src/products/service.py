from decimal import Decimal
from typing import TYPE_CHECKING, NamedTuple
from urllib.parse import parse_qs, urlparse

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.exceptions import NotFoundError
from src.products.exceptions import ProductParserError

from . import models, schemas

if TYPE_CHECKING:
    from ..catalogs import service as catalog_service


class ParsedProduct(NamedTuple):
    parsed_breadcrumb_catalogs: "catalog_service.ParsedBreadcrumbCatalogs"
    product: schemas.Product


async def parse_product_by_code(
    *, driver: Chrome, async_session: AsyncSession, code: int
) -> ParsedProduct:
    from ..catalogs import service as catalog_service

    try:
        driver.get(f"https://www.flip.kz/catalog?prod={code}")
        wait = WebDriverWait(driver, 5)
        info_container = wait.until(visibility_of_element_located((By.ID, "prod")))
        images_container = info_container.find_element(By.CLASS_NAME, "prod_img")
        data_container = images_container.find_element(
            By.XPATH, "following-sibling::*[1]"
        )
        name = data_container.find_element(By.TAG_NAME, "h1").text
        description = data_container.find_element(By.TAG_NAME, "p").text or None
        price = Decimal(
            "".join(
                filter(
                    str.isdigit,
                    "".join(
                        data_container.find_element(
                            By.CLASS_NAME, "text_att"
                        ).text.split()
                    ),
                )
            )
        )
        product = schemas.ProductCreate(
            code=code, name=name, description=description, price=price, catalog_id=0
        )
        parsed_breadcrumb_catalogs = await catalog_service.parse_breadcrumb_catalogs(
            driver
        )
        for image_element in images_container.find_elements(By.TAG_NAME, "img"):
            url = image_element.get_attribute("src")
            description = image_element.get_attribute("alt")
            product.images.append(
                schemas.ProductImageCreate(url=url, description=description)
            )
        return ParsedProduct(parsed_breadcrumb_catalogs, product)
    except Exception as exception:
        raise ProductParserError(f"Unexpected error: {exception}")


async def parse_product_by_id(
    *, driver: Chrome, async_session: AsyncSession, id: int
) -> ParsedProduct:
    product = await get_product_by_id(async_session, id)
    if product is None:
        raise NotFoundError(f"Product with id {id} - not found")
    return await parse_product_by_code(
        driver=driver, async_session=async_session, code=product.code
    )


async def parse_product_by_url(
    *, driver: Chrome, async_session: AsyncSession, url: str
) -> ParsedProduct:
    code = parse_qs(urlparse(url).query).get("prod")
    if code is None:
        raise ProductParserError("There is no 'prod' in query parameters")
    return await parse_product_by_code(
        driver=driver, async_session=async_session, code=int(code[0])
    )


async def get_product_by_id(async_session: AsyncSession, id: int):
    result = await async_session.execute(
        select(models.Product)
        .options(selectinload(models.Product.images))
        .where(models.Product.id == id)
    )
    product = result.scalars().first()
    if product is None:
        raise NotFoundError
    return product


async def get_product_by_code(async_session: AsyncSession, code: int):
    result = await async_session.execute(
        select(models.Product)
        .options(selectinload(models.Product.images))
        .where(models.Product.code == code)
    )
    product = result.scalars().first()
    if product is None:
        raise NotFoundError
    return product


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


async def update_product_by_id(
    async_session: AsyncSession,
    id: int,
    product_in: schemas.ProductUpdate,
):
    db_product = await get_product_by_id(async_session, id)
    if not db_product:
        return None
    update_data = product_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    async_session.add(db_product)
    await async_session.commit()
    return await get_product_by_id(async_session, id)


async def delete_product_by_id(async_session: AsyncSession, id: int):
    db_product = await get_product_by_id(async_session, id)
    if not db_product:
        return None
    await async_session.delete(db_product)
    return db_product


async def upsert_product_by_code(
    async_session: AsyncSession,
    product_in: schemas.ProductCreate,
    *,
    commit: bool = True,
):
    try:

        db_product = await get_product_by_code(async_session, product_in.code)
    except NotFoundError:
        product_data = product_in.model_dump(exclude={"images"})
        db_product = models.Product(**product_data)
        if product_in.images:
            for image_in in product_in.images:
                db_product.images.append(models.ProductImage(**image_in.model_dump()))
    else:
        update_data = product_in.model_dump(exclude={"images"})
        for key, value in update_data.items():
            setattr(db_product, key, value)

        db_product.images.clear()
        if product_in.images:
            for image_in in product_in.images:
                db_product.images.append(models.ProductImage(**image_in.model_dump()))

    async_session.add(db_product)
    if commit:
        await async_session.commit()
        await async_session.refresh(db_product)
    else:
        await async_session.flush([db_product])
    return db_product


async def upsert_parsed_product(
    *, async_session: AsyncSession, parsed_product: ParsedProduct
) -> schemas.Product:
    from ..catalogs import service as catalog_service

    catalogs = await catalog_service.upsert_parsed_breadcrumb_catalogs(
        async_session=async_session,
        parsed_breadcrumb_catalogs=parsed_product.parsed_breadcrumb_catalogs,
        commit=False,
    )
    product = parsed_product.product
    product.catalog_id = catalogs[
        parsed_product.parsed_breadcrumb_catalogs.last_catalog_code
    ].id
    return await upsert_product_by_code(async_session, product)


async def upsert_parsed_product_by_code(
    *, driver: Chrome, async_session: AsyncSession, code: int
) -> schemas.Product:
    return await upsert_parsed_product(
        async_session=async_session,
        parsed_product=await parse_product_by_code(
            driver=driver, async_session=async_session, code=code
        ),
    )


async def upsert_parsed_product_by_url(
    *, driver: Chrome, async_session: AsyncSession, url: str
) -> schemas.Product:
    return await upsert_parsed_product(
        async_session=async_session,
        parsed_product=await parse_product_by_url(
            driver=driver, async_session=async_session, url=url
        ),
    )


async def upsert_parsed_product_by_id(
    *, driver: Chrome, async_session: AsyncSession, id: int
) -> schemas.Product:
    return await upsert_parsed_product(
        async_session=async_session,
        parsed_product=await parse_product_by_id(
            driver=driver, async_session=async_session, id=id
        ),
    )
