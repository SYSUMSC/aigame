from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AIGame"
    API_ADMIN_STR: str = "/api/admin"
    API_USER_STR: str = "/api/user"
    SECRET_KEY: str = "xy3"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URI: str = "sqlite+aiosqlite:///./test.db"

settings = Settings()