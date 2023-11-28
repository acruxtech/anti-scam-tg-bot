from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.repository import SQLAlchemyRepository


class ScammerReport(Base):
    __tablename__ = "scammers_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=True)
    datetime_reported: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    is_reviewed: Mapped[bool] = mapped_column(default=False)
    reviewer_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    datetime_reviewed: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    explanation: Mapped[str] = mapped_column(nullable=True)
    decision: Mapped[bool] = mapped_column(nullable=True)

    reported_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    scammer_id: Mapped[int] = mapped_column(ForeignKey("scammers.id"))

    reported_user: Mapped["User"] = relationship(back_populates="scammers_reports")
    scammer: Mapped["Scammer"] = relationship(back_populates="scammers_reports")
    scammer_media: Mapped[list["ScammerMedia"]] = relationship(back_populates="scammers_reports")


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

    scammers_reports: Mapped[list[ScammerReport]] = relationship(back_populates="scammer")


class ScammerMedia(Base):
    __tablename__ = "scammers_reports_media"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column()
    file_id: Mapped[str] = mapped_column()

    scammers_reports_id: Mapped[int] = mapped_column(ForeignKey("scammers_reports.id"))
    scammers_reports: Mapped[ScammerReport] = relationship(back_populates="scammer_media")


scammers_repository = SQLAlchemyRepository(Scammer)

scammers_reports_repository = SQLAlchemyRepository(ScammerReport)

scam_media_repository = SQLAlchemyRepository(ScammerMedia)
