from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mode: str
    postgres_dsn: str

    model_config = SettingsConfigDict()


settings = Settings()
