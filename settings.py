from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE: str
    BACKEND: str
    ADMIN_HEADER: str

    class Config:
        env_file = ".env"