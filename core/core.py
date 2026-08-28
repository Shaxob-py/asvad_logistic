from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientTimeout
from pydantic_settings import BaseSettings

session = AiohttpSession(
    timeout=ClientTimeout(total=300)
)


class Settings(BaseSettings):
    DB_DATABASE: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    BOT_TOKEN: str

    GROUP_CHAT_ID_ADLER: int
    GROUP_CHAT_ID_GATTER: int

    class Config:
        env_file = ".env"

    def postgres_async_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:"
                f"{self.DB_PORT}/{self.DB_DATABASE}")


settings = Settings()
dp = Dispatcher()
bot = Bot(token=settings.BOT_TOKEN)
