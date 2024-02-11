from typing import Any, Awaitable, Callable, Dict, TypeVar

from aiogram.types import TelegramObject

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
import asyncio
import datetime


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 5, interval: int = 60):
        self.limit = limit
        self.interval = interval
        self.storage = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        user_id = user.id
        if user_id not in self.storage:
            self.storage[user_id] = []
        now = datetime.datetime.now()
        self.storage[user_id] = [t for t in self.storage[user_id] if (now - t).seconds < self.interval]

        print(len(self.storage[user_id]))

        if len(self.storage[user_id]) >= self.limit:
            if isinstance(event, types.Message):
                await event.answer("Слишком много запросов, попробуйте позже")
            elif isinstance(event, types.CallbackQuery):
                await event.message.answer("Слишком много запросов, попробуйте позже")
            return

        self.storage[user_id].append(now)
        return await handler(event, data)
