from datetime import datetime

from sqlalchemy import BigInteger, JSON, ForeignKey, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Table


class Base(DeclarativeBase):
    pass

user_group_association = Table(
    "user_group_association",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.telegram_id"), primary_key=True),
    Column("group_id", BigInteger, ForeignKey("groups.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()
    language: Mapped[str | None] = mapped_column()

    groups = relationship("Group", secondary=user_group_association, back_populates="members")
    owned_groups = relationship("Group", back_populates="user", foreign_keys="[Group.owned_by]")

class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    owned_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))

    members = relationship("User", secondary=user_group_association, back_populates="groups")
    subgroups = relationship("Subgroup", back_populates="group")
    user = relationship("User", back_populates="owned_groups", foreign_keys=[owned_by])

class Subgroup(Base):
    __tablename__ = "subgroups"

    sg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))

    group = relationship("Group", back_populates="subgroups")
    events = relationship("Event", back_populates="subgroup")

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("subgroups.sg_id"))
    name: Mapped[str] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column()
    comment: Mapped[str] = mapped_column()

    subgroup = relationship("Subgroup", back_populates="events")



