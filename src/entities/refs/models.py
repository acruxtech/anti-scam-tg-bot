from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.repository import SQLAlchemyRepository
from src.db.database import Base


class Ref(Base):
    __tablename__ = "refs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()

    users: Mapped[list["User"]] = relationship(lazy='subquery')


ref_repository = SQLAlchemyRepository(Ref)
