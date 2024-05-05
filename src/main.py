import os
import logging
import asyncio

from aiogram import Bot, Dispatcher

from src.middlewares.limit import RateLimitMiddleware
from src.handlers.systems import get_start, get_stop
from src.config import BOT_TOKEN
from src.handlers import basic, scammer, contact, admin, chat, add
from src.entities.scammers.service import scammers_repository

from data import scammer_ids_and_usernames
from src.repository import IntegrityException

from src.database import engine, Base


async def start():
    if(os.path.isfile('bot.log')):
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

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        await scammers_repository.create_many(scammer_ids_and_usernames)
    except IntegrityException as e:
        print("Скамеры уже добавлены в базу")

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

    dp = Dispatcher()

    dp.message.middleware.register(RateLimitMiddleware(40, 60))
    dp.callback_query.middleware.register(RateLimitMiddleware(40, 60))
    
    dp.include_router(admin.router)
    dp.include_router(scammer.scammer_router)
    dp.include_router(basic.basic_router)
    dp.include_router(contact.router)
    dp.include_router(chat.router)
    dp.include_router(add.router)

    dp.startup.register(get_start)
    dp.shutdown.register(get_stop)

    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query", "my_chat_member", "inline_query", "chosen_inline_result"])
    finally:
        await bot.session.close()

asyncio.run(start())
