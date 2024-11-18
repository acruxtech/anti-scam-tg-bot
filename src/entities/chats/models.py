from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.db.repository import SQLAlchemyRepository
from src.db.database import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column()


chat_repository = SQLAlchemyRepository(Chat)
