from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mode: str
    postgres_dsn: str
    flip_catalog_url: str = "https://www.flip.kz/catalog"

    model_config = SettingsConfigDict()


settings = Settings()
