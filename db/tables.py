from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column



class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()
    language: Mapped[str | None] = mapped_column()

class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    owner_id: Mapped[int] = mapped_column(BigInteger)
    admin_ids: Mapped[list[int] | None] = mapped_column(BigInteger)
