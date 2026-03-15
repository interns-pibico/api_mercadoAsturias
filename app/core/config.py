from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "Mercado Asturias API"

    class Config:
        env_file = ".env"


settings = Settings()