import logging
from functools import lru_cache

from pydantic.v1 import BaseSettings


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(threadName)s] %(levelname)-5s %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S.%f",
)



class Settings(BaseSettings):
    GITHUB_TOKEN: str
    TOKEN: str

    class Config:
        env_file = f".env"


@lru_cache
def get_settings():
    return Settings()  # type: ignore
