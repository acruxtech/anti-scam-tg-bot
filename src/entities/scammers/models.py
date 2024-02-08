from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.repository import SQLAlchemyRepository


class Scammer(Base):
    __tablename__ = "scammers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    language_code: Mapped[str] = mapped_column(nullable=True)
    datetime_first: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    datetime_confirmed: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    number_requests: Mapped[int] = mapped_column(default=1)
    is_scam: Mapped[bool] = mapped_column(default=False, nullable=True)

    scammer_media: Mapped[list["ScammerMedia"]] = relationship(back_populates="scammer")
    proofs: Mapped[list["Proof"]] = relationship(back_populates="scammer")


class ScammerMedia(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column()
    file_id: Mapped[str] = mapped_column()
    scammer_id: Mapped[int] = mapped_column(ForeignKey("scammers.id", ondelete="CASCADE"))
    proof_id: Mapped[int] = mapped_column(ForeignKey("proofs.id", ondelete="CASCADE"))

    scammer: Mapped[Scammer] = relationship(back_populates="scammer_media")
    proof: Mapped["Proof"] = relationship(back_populates="scammer_media")


class Proof(Base):
    __tablename__ = "proofs"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    decision: Mapped[bool] = mapped_column(default=False)

    scammer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("scammers.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    moderator_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    scammer: Mapped[Scammer] = relationship(back_populates="proofs")
    scammer_media: Mapped[list[ScammerMedia]] = relationship(back_populates="proof")
    user: Mapped["User"] = relationship(back_populates="proofs")


scammers_repository = SQLAlchemyRepository(Scammer)

media_repository = SQLAlchemyRepository(ScammerMedia)

proof_repository = SQLAlchemyRepository(Proof)
