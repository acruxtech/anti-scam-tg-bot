from datetime import datetime

from src.repository import RepositoryInterface, IntegrityException

from src.entities.chats.models import Chat, chat_repository
from src.entities.chats.schemas import ChatScheme


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
        try:
            return await self.repository.delete(id)
        except BaseException:
            ...

    async def get_chats(self):
        try:
            return await self.repository.get_list()
        except BaseException:
            ...


chat_service = ChatService(chat_repository)
