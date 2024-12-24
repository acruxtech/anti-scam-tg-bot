from contextlib import suppress
from datetime import datetime

from src.core.schemas.chat import ChatScheme
from src.db.errors import DBError
from src.db.models import Chat
from src.db.repository import RepositoryInterface


class ChatService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def add_chat(self, chat: ChatScheme):
        try:
            await self.repository.create(chat.model_dump())
        except DBError:
            update_chat = chat.model_dump()
            update_chat["datetime_last"] = datetime.now()
            await self.repository.update(update_chat, chat.id)

    async def delete_chat(self, _id: int):
        return await self.repository.delete(_id)

    async def get_chats(self):
        return await self.repository.get_list()


chat_service = ChatService(Chat.repository())
