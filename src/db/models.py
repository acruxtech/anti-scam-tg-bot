from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import BaseModel
from src.db.repository import Repository


class BaseModelRepository(BaseModel):
    __abstract__ = True

    @classmethod
    def repository(cls) -> Repository:
        return Repository(cls)


class Chat(BaseModelRepository):
    __tablename__ = "chats"

    title: Mapped[str] = mapped_column()


class Ref(BaseModelRepository):
    __tablename__ = "refs"

    title: Mapped[str] = mapped_column()
    users: Mapped[list["User"]] = relationship(lazy='subquery')


class User(BaseModelRepository):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    language_code: Mapped[str] = mapped_column(nullable=True)
    is_premium: Mapped[bool] = mapped_column(nullable=True)
    is_bot: Mapped[bool] = mapped_column(nullable=True)
    is_blocked: Mapped[bool] = mapped_column()
    ref_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("refs.id", ondelete="CASCADE"), nullable=True)
    datetime_first: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    datetime_last: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    proofs: Mapped[list["Proof"]] = relationship(back_populates="user")


class Scammer(BaseModelRepository):
    __tablename__ = "scammers"

    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    language_code: Mapped[str] = mapped_column(nullable=True)
    datetime_first: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    datetime_confirmed: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    number_requests: Mapped[int] = mapped_column(default=1)
    is_scam: Mapped[bool] = mapped_column(default=False, nullable=True)

    scammer_media: Mapped[list["ScammerMedia"]] = relationship(back_populates="scammer")
    proofs: Mapped[list["Proof"]] = relationship(back_populates="scammer")


class ScammerMedia(BaseModelRepository):
    __tablename__ = "media"

    type: Mapped[str] = mapped_column()
    file_id: Mapped[str] = mapped_column()
    scammer_id: Mapped[int] = mapped_column(ForeignKey("scammers.id", ondelete="CASCADE"))
    proof_id: Mapped[int] = mapped_column(ForeignKey("proofs.id", ondelete="CASCADE"))

    scammer: Mapped[Scammer] = relationship(back_populates="scammer_media")
    proof: Mapped["Proof"] = relationship(back_populates="scammer_media")


class Proof(BaseModelRepository):
    __tablename__ = "proofs"

    text: Mapped[str] = mapped_column()
    decision: Mapped[bool] = mapped_column(default=False)

    scammer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("scammers.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    moderator_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    scammer: Mapped[Scammer] = relationship(back_populates="proofs")
    scammer_media: Mapped[list[ScammerMedia]] = relationship(back_populates="proof")
    user: Mapped["User"] = relationship(back_populates="proofs")


class UserInfo(BaseModelRepository):
    __tablename__ = "user_info"

    username: Mapped[str] = mapped_column()
    link: Mapped[str] = mapped_column()


class ContactMessage(BaseModelRepository):
    __tablename__ = "contact_messages"

    contact_id: Mapped[int] = mapped_column(BigInteger)
    message: Mapped[str] = mapped_column()
    datetime_create: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    answer: Mapped[str] = mapped_column(nullable=True)
    is_answered: Mapped[bool] = mapped_column(default=False)
    answered_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    datetime_answer: Mapped[datetime] = mapped_column(DateTime, nullable=True)
