from contextlib import suppress
from datetime import datetime

from src.db.repository import RepositoryInterface, IntegrityException

from src.entities.chats.models import Chat, chat_repository


class ChatService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def add_chat(self, chat: Chat):
        try:
            await self.repository.create(chat.model_dump())
        except IntegrityException:
            update_chat = chat.model_dump()
            update_chat["datetime_last"] = datetime.now()
            await self.repository.update(update_chat, chat.id)

    async def delete_chat(self, id: int):
        with suppress(BaseException):
            return await self.repository.delete(id)

    async def get_chats(self):
        with suppress(BaseException):
            return await self.repository.get_list()


chat_service = ChatService(chat_repository)
