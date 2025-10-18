from datetime import datetime

from sqlalchemy import BigInteger, JSON, ForeignKey, Column, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Table


class Base(DeclarativeBase):
    pass

user_group_association = Table(
    "user_group_association",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()

    groups = relationship("Group", secondary=user_group_association, back_populates="members")
    owned_groups = relationship("Group", back_populates="user", foreign_keys="[Group.owned_by]")
    join_requests = relationship("JoinRequest", back_populates="user")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    owned_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))

    members = relationship(
        "User",
        secondary=user_group_association,
        back_populates="groups",
        passive_deletes=True  # учитывает CASCADE в user_group_association
    )
    subgroups = relationship(
        "Subgroup",
        back_populates="group",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    join_requests = relationship(
        "JoinRequest",
        back_populates="group",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    user = relationship("User", back_populates="owned_groups", foreign_keys=[owned_by])

class Subgroup(Base):
    __tablename__ = "subgroups"

    sg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))

    group = relationship("Group", back_populates="subgroups")
    events = relationship("Event", back_populates="subgroup", cascade="all, delete-orphan", passive_deletes=True)

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sg_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("subgroups.sg_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column()
    comment: Mapped[str] = mapped_column()

    subgroup = relationship("Subgroup", back_populates="events")

class JoinRequest(Base):
    __tablename__ = "join_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    group_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="join_requests")
    group = relationship("Group", back_populates="join_requests")

class SoloReminder(Base):
    __tablename__ = "personal_reminders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column()
    notify_time: Mapped[datetime] = mapped_column()

    user = relationship("User", backref="personal_reminders")
