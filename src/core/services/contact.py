from datetime import datetime

from src.db.models import ContactMessage
from src.db.repository import RepositoryInterface


class ContactMessageService:

    def __init__(self, repository: RepositoryInterface):
        self.repository = repository

    async def create_contact_message(self, user_id: int, message: str):
        contact_message = {
            "contact_id": user_id,
            "message": message
        }
        contact_message = await self.repository.create(contact_message)
        return contact_message

    async def answer_contact_message(self, contact_message_id: int, answer: str, answered_id: int):
        data = {
            "answer": answer,
            "answered_id": answered_id,
            "datetime_answer": datetime.now(),
            "is_answered": True
        }
        return await self.repository.update(data, contact_message_id)


contact_message_service = ContactMessageService(ContactMessage.repository())
