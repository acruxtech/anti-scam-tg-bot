import logging
import asyncio

from aiogram import Bot, Dispatcher

from src.handlers.systems import get_start, get_stop
from src.config import BOT_TOKEN
from src.handlers import basic, scammer, contact


async def start():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    )

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

    dp = Dispatcher()

    dp.include_router(scammer.scammer_router)
    dp.include_router(basic.basic_router)
    dp.include_router(contact.router)

    dp.startup.register(get_start)
    dp.shutdown.register(get_stop)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

asyncio.run(start())
