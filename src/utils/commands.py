from aiogram import Bot
from aiogram.types import BotCommand


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
