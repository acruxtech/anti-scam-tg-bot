from aiogram import Bot
from aiogram.types import BotCommand

from src.config import ADMIN_ID


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Главное меню'
        ),
        BotCommand(
            command='add_to_channel',
            description='Добавить в канал'
        )
    ]

    await bot.set_my_commands(commands)


async def get_start(bot: Bot):
    await set_commands(bot)
    await bot.send_message(ADMIN_ID, 'Бот запущен!')


async def get_stop(bot: Bot):
    await bot.send_message(ADMIN_ID, 'Бот выключен!')
