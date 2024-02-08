from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.repository import SQLAlchemyRepository
from src.database import Base
from src.entities.scammers.models import Proof


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    language_code: Mapped[str] = mapped_column(nullable=True)
    is_premium: Mapped[bool] = mapped_column(nullable=True)
    is_bot: Mapped[bool] = mapped_column(nullable=True)
    datetime_first: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    datetime_last: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    proofs: Mapped[list[Proof]] = relationship(back_populates="user")


user_repository = SQLAlchemyRepository(User)
