import asyncio
from typing import Callable, Dict, Any, Awaitable

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 5, interval: int = 60):
        self.limit = limit
        self.interval = interval
        self.storage = {}

    async def __call__(self, bot, update, data):
        if isinstance(update, types.Message):
            await self.on_process_message(update, data)
        elif isinstance(update, types.CallbackQuery):
            await self.on_process_callback_query(update, data)

    async def on_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        if user_id not in self.storage:
            self.storage[user_id] = []
        now = message.date
        self.storage[user_id] = [t for t in self.storage[user_id] if now - t < self.interval]  # Clean old timestamps
        if len(self.storage[user_id]) >= self.limit:
            await message.reply("You are sending messages too frequently. Please wait a moment.")
            raise asyncio.CancelledError()  # Cancel the handler
        self.storage[user_id].append(now)

    async def on_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        user_id = callback_query.from_user.id
        if user_id not in self.storage:
            self.storage[user_id] = []
        now = callback_query.message.date
        self.storage[user_id] = [t for t in self.storage[user_id] if now - t < self.interval]  # Clean old timestamps
        if len(self.storage[user_id]) >= self.limit:
            await callback_query.answer("You are sending messages too frequently. Please wait a moment.")
            raise asyncio.CancelledError()  # Cancel the handler
        self.storage[user_id].append(now)

