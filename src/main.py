import os
import logging
import asyncio

from aiogram import Bot, Dispatcher

from src.core.middlewares.limit import RateLimitMiddleware
from src.core.utils.systems import get_start, get_stop
from src.core.handlers import admin, basic, contact, inline, add, scammer, chat
from src.core.utils.variables import bot, scheduler
from src.db.errors import DBError
from src.db.models import Scammer

from assets.data import scammer_ids_and_usernames

from src.db.database import engine
from src.db.base import Base


async def start():
    if os.path.isfile('bot.log'):
        os.remove('bot.log')

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
        encoding="UTF-8",
        handlers=[
            logging.FileHandler("bot.log"),
            logging.StreamHandler()
        ]
    )

    scheduler.start()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        await Scammer.repository().create_many(scammer_ids_and_usernames)
    except DBError:
        print("Скамеры уже добавлены в базу")

    dp = Dispatcher()

    dp.message.middleware.register(RateLimitMiddleware(40, 60))
    dp.callback_query.middleware.register(RateLimitMiddleware(40, 60))
    
    dp.include_router(admin.router)
    dp.include_router(scammer.scammer_router)
    dp.include_router(basic.basic_router)
    dp.include_router(contact.router)
    dp.include_router(chat.router)
    dp.include_router(add.router)
    dp.include_router(inline.router)

    dp.startup.register(get_start)
    dp.shutdown.register(get_stop)

    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query", "my_chat_member", "chat_member", "inline_query", "chosen_inline_result"])
    finally:
        await bot.session.close()

asyncio.run(start())
