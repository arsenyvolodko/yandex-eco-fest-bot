import asyncio

from aiogram import Bot

from yandex_eco_fest_bot.core.config import BOT_TOKEN
from yandex_eco_fest_bot.core.logging import setup_logging
from yandex_eco_fest_bot.db.core.db_manager import db_manager


async def main() -> None:
    await db_manager.init()
    from yandex_eco_fest_bot.bot.bot import dp
    await dp.start_polling(bot)


bot = Bot(token=BOT_TOKEN)
loop = asyncio.new_event_loop()


if __name__ == "__main__":
    setup_logging()
    loop.run_until_complete(main())
