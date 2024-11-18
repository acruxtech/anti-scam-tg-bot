from aiogram.filters import Filter
from aiogram.types import Message

from src.config import OWNER_IDS


class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in OWNER_IDS
