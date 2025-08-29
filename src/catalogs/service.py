import collections
from typing import TYPE_CHECKING, NamedTuple
from urllib.parse import parse_qs, urlparse

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas

if TYPE_CHECKING:
    from ..products import schemas as product_schemas


class ParsedBreadcrumbCatalogs(NamedTuple):
    catalog_map: dict[int, schemas.CatalogCreate]
    catalog_parent_map: dict[int, int | None]
    last_catalog_code: int | None

    def in_order(self) -> list[schemas.CatalogCreate]:
        """
        Возвращает список каталогов, отсортированный в топологическом порядке
        (родители идут перед дочерними элементами).

        Используется алгоритм Кана.
        """
        # Если карт нет, возвращаем пустой список
        if not self.catalog_map:
            return []

        # 1. Подготовка: Создаем карту дочерних элементов и считаем "входящие степени"
        # (т.е. количество родителей у каждого каталога)

        # children_map: {parent_code: [child_code_1, child_code_2]}
        children_map: dict[int, list[int]] = {code: [] for code in self.catalog_map}
        # in_degrees: {code: count_of_parents}
        in_degrees: dict[int, int] = {code: 0 for code in self.catalog_map}

        for child_code, parent_code in self.catalog_parent_map.items():
            if parent_code is not None:
                # Если родитель есть, добавляем ребенка в список детей родителя
                children_map[parent_code].append(child_code)
                # и увеличиваем счетчик родителей для ребенка
                in_degrees[child_code] += 1

        # 2. Находим корневые элементы: это каталоги без родителей (in_degree == 0)
        # и добавляем их в очередь для обработки
        queue = collections.deque(
            [code for code, degree in in_degrees.items() if degree == 0]
        )

        sorted_catalogs: list[schemas.CatalogCreate] = []

        while queue:
            current_code = queue.popleft()

            sorted_catalogs.append(self.catalog_map[current_code])

            for child_code in children_map.get(current_code, []):
                in_degrees[child_code] -= 1
                if in_degrees[child_code] == 0:
                    queue.append(child_code)

        if len(sorted_catalogs) != len(self.catalog_map):
            raise ValueError("Обнаружен цикл в зависимостях каталогов.")

        return sorted_catalogs

    def union(self, other: "ParsedBreadcrumbCatalogs") -> "ParsedBreadcrumbCatalogs":
        return ParsedBreadcrumbCatalogs(
            self.catalog_map | other.catalog_map,
            self.catalog_parent_map | other.catalog_parent_map,
            None,
        )


async def parse_breadcrumb_catalogs(driver: Chrome, /) -> ParsedBreadcrumbCatalogs:
    breadcrumb_catalogs_container = driver.find_element(By.CLASS_NAME, "krohi")
    catalog_map = {}
    catalog_parent_map = {}
    previous_code = None
    for breadcrumb in breadcrumb_catalogs_container.find_elements(By.TAG_NAME, "a"):
        code = int(
            parse_qs(urlparse(breadcrumb.get_attribute("href")).query)["subsection"][0]
        )
        catalog_parent_map[code] = previous_code
        name = breadcrumb.get_attribute("title")
        catalog_map[code] = schemas.CatalogCreate(code=code, name=name)
        previous_code = code
    return ParsedBreadcrumbCatalogs(catalog_map, catalog_parent_map, previous_code)


class ParsedCatalogProducts(NamedTuple):
    parsed_breadcrumb_catalogs: ParsedBreadcrumbCatalogs
    product_catalog_map: dict[int, int]
    products: list["product_schemas.ProductCreate"]


async def parse_catalog_products_by_code(
    *,
    driver: Chrome,
    async_session: AsyncSession,
    code: int,
    page: int,
    limit: int,
) -> ParsedCatalogProducts:
    from ..products import service as product_service

    driver.get(f"https://www.flip.kz/catalog?subsection={code}&page={page}")
    product_codes = []
    wait = WebDriverWait(driver, 5)
    products_container = wait.until(
        visibility_of_element_located((By.CLASS_NAME, "good-grid"))
    )
    for number, product_element in enumerate(
        products_container.find_elements(By.CLASS_NAME, "new-product")
    ):
        if number > limit:
            break
        product_link_element = product_element.find_element(By.TAG_NAME, "a")
        product_url = product_link_element.get_attribute("href")
        product_code = parse_qs(urlparse(product_url).query)["prod"][0]
        product_codes.append(product_code)
    parsed_breadcrumb_catalogs = await parse_breadcrumb_catalogs(driver)
    product_catalog_map: dict[int, int] = {}
    products = []
    for product_code in product_codes:
        print(product_code)
        parsed_product = await product_service.parse_product_by_code(
            driver=driver, async_session=async_session, code=product_code
        )
        product_catalog_map[parsed_product.product.code] = (
            parsed_product.parsed_breadcrumb_catalogs.last_catalog_code
        )
        parsed_breadcrumb_catalogs = parsed_breadcrumb_catalogs.union(
            parsed_product.parsed_breadcrumb_catalogs
        )
        products.append(parsed_product.product)
    return ParsedCatalogProducts(
        parsed_breadcrumb_catalogs, product_catalog_map, products
    )


async def parse_catalog_products_by_id(
    *,
    driver: Chrome,
    async_session: AsyncSession,
    id: int,
    page: int,
    limit: int,
) -> ParsedCatalogProducts:

    catalog = await get_catalog_by_id(async_session, id)
    if catalog is None:
        raise
    return await parse_catalog_products_by_code(
        driver=driver,
        async_session=async_session,
        code=catalog.code,
        page=page,
        limit=limit,
    )


async def parse_catalog_products_by_url(
    *,
    driver: Chrome,
    async_session: AsyncSession,
    url: str,
    page: int,
    limit: int,
) -> ParsedCatalogProducts:
    code = parse_qs(urlparse(url).query).get("subsection")
    if code is None:
        raise
    return await parse_catalog_products_by_code(
        driver=driver,
        async_session=async_session,
        code=int(code[0]),
        page=page,
        limit=limit,
    )


async def get_catalog_by_id(async_session: AsyncSession, id: int):
    result = await async_session.execute(
        select(models.Catalog).where(models.Catalog.id == id)
    )
    return result.scalars().first()


async def get_catalog_by_code(async_session: AsyncSession, code: int):
    result = await async_session.execute(
        select(models.Catalog).where(models.Catalog.code == code)
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


async def update_catalog_by_id(
    async_session: AsyncSession,
    id: int,
    catalog_in: schemas.CatalogUpdate,
):
    db_catalog = await get_catalog_by_id(async_session, id)
    if not db_catalog:
        return None
    update_data = catalog_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_catalog, key, value)
    async_session.add(db_catalog)
    await async_session.commit()
    return await get_catalog_by_id(async_session, id)


async def delete_catalog_by_id(async_session: AsyncSession, id: int):
    db_catalog = await get_catalog_by_id(async_session, id)
    if not db_catalog:
        return None
    await async_session.delete(db_catalog)
    await async_session.commit()
    return db_catalog


async def upsert_catalog_by_code(
    async_session: AsyncSession,
    catalog_in: schemas.CatalogCreate,
    *,
    commit: bool = True,
):
    db_catalog = await get_catalog_by_code(async_session, catalog_in.code)

    if db_catalog:
        update_data = catalog_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_catalog, key, value)
    else:
        db_catalog = models.Catalog(**catalog_in.model_dump())

    async_session.add(db_catalog)
    if commit:
        await async_session.commit()
        await async_session.refresh(db_catalog)
    else:
        await async_session.flush([db_catalog])
    return db_catalog


async def upsert_parsed_breadcrumb_catalogs(
    async_session: AsyncSession, parsed_breadcrumb_catalogs: ParsedBreadcrumbCatalogs, commit: bool = True
) -> dict[int, schemas.Catalog]:
    saved = {}
    for catalog in parsed_breadcrumb_catalogs.in_order():
        parent = saved.get(parsed_breadcrumb_catalogs.catalog_parent_map[catalog.code])
        if parent is not None:
            catalog.parent_id = parent.id
        saved[catalog.code] = await upsert_catalog_by_code(
            async_session, catalog, commit=False
        )
    if commit:
        await async_session.commit()
        for catalog in saved.values():
            await async_session.refresh(catalog)
    return saved


async def upsert_parsed_catalog_products_by_id(
    *,
    driver: Chrome,
    async_session: AsyncSession,
    id: int,
    page: int,
    limit: int,
):
    return await upsert_parsed_catalog_products(
        async_session=async_session,
        parsed_catalog_products=await parse_catalog_products_by_id(
            driver=driver,
            async_session=async_session,
            id=id,
            page=page,
            limit=limit,
        ),
    )


async def upsert_parsed_catalog_products_by_url(
    *,
    driver: Chrome,
    async_session: AsyncSession,
    url: str,
    page: int,
    limit: int,
):
    return await upsert_parsed_catalog_products(
        async_session=async_session,
        parsed_catalog_products=await parse_catalog_products_by_url(
            driver=driver,
            async_session=async_session,
            url=url,
            page=page,
            limit=limit,
        ),
    )


async def upsert_parsed_catalog_products_by_code(
    *,
    driver: Chrome,
    async_session: AsyncSession,
    code: int,
    page: int,
    limit: int,
):
    return await upsert_parsed_catalog_products(
        async_session=async_session,
        parsed_catalog_products=await parse_catalog_products_by_code(
            driver=driver,
            async_session=async_session,
            code=code,
            page=page,
            limit=limit,
        ),
    )


async def upsert_parsed_catalog_products(
    *, async_session: AsyncSession, parsed_catalog_products: ParsedCatalogProducts
) -> None:
    from ..products import service as product_service

    catalogs = await upsert_parsed_breadcrumb_catalogs(
        async_session=async_session,
        parsed_breadcrumb_catalogs=parsed_catalog_products.parsed_breadcrumb_catalogs,
        commit=False
    )
    for product in parsed_catalog_products.products:
        product.catalog_id = catalogs[
            parsed_catalog_products.product_catalog_map[product.code]
        ].id
        await product_service.upsert_product_by_code(async_session, product, commit=False)
    await async_session.commit()
