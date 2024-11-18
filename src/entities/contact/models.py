from datetime import datetime

from src.db.database import Base
from src.db.repository import SQLAlchemyRepository

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(BigInteger)
    message: Mapped[str] = mapped_column()
    datetime_create: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    answer: Mapped[str] = mapped_column(nullable=True)
    is_answered: Mapped[bool] = mapped_column(default=False)
    answered_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    datetime_answer: Mapped[datetime] = mapped_column(DateTime, nullable=True)


contact_manage_repository = SQLAlchemyRepository(ContactMessage)
