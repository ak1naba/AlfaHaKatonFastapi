from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@db:5432/openrouter_db"
    REDIS_URL: str = "redis://cache:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
