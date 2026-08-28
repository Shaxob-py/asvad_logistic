import asyncio

from core.core import dp, bot
from db.base import db
from handler.admin import router_admin
from handler.group import router_group


async def main() -> None:
    await db.create_all()
    dp.include_router(router_group)
    dp.include_router(router_admin)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
