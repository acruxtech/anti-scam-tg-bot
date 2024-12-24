import pytz
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import BOT_TOKEN

job_defaults = {
    "max_instances": 10000
}

scheduler = AsyncIOScheduler(
    job_defaults=job_defaults,
    timezone=pytz.timezone('Europe/Moscow'),
)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
