from collections.abc import AsyncIterator

import undetected_chromedriver
from selenium.webdriver import Chrome
from sqlalchemy.ext.asyncio import AsyncSession

from . import database


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with database.AsyncSession() as session:
        yield session


async def get_driver() -> AsyncIterator[Chrome]:
    options = undetected_chromedriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = undetected_chromedriver.Chrome(options)
    try:
        yield driver
    finally:
        driver.quit()
