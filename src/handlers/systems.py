from aiogram import Bot

from ..config import ADMIN_ID
from ..utils.commands import set_commands


async def get_start(bot: Bot):
    await set_commands(bot)
    await bot.send_message(ADMIN_ID, 'Бот запущен!')


async def get_stop(bot: Bot):
    await bot.send_message(ADMIN_ID, 'Бот выключен!')
