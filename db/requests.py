from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, selectinload
from db.tables import User, Group, Subgroup, Event
from config.config import load_config
from sqlalchemy import select, delete, update
import asyncio
db_config = load_config()

engine = create_async_engine(url=db_config.postgres.url)

AsyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def create_user(telegram_id: int, first_name: str, last_name: str | None = None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
        if result.scalar_one_or_none() is None:
            user = User(telegram_id=telegram_id, first_name=first_name, last_name=last_name)
            session.add(user)
            await session.commit()

async def get_user(telegram_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = await session.execute(select(User).where(User.telegram_id == telegram_id))
            return user.scalar_one_or_none()


async def create_group(name: str, owned_by: int):
    async with AsyncSessionLocal() as session:
        group = Group(name=name, owned_by=owned_by)
        session.add(group)
        await session.commit()
        return group

async def create_subgroup(name: str, group_id: int):
    async with AsyncSessionLocal() as session:
        subgroup = Subgroup(name=name, group_id=group_id)
        session.add(subgroup)
        await session.commit()


async def set_user_language(user_id: int, language: str):
    stmt = select(User).where(User.telegram_id == user_id)
    async with AsyncSessionLocal() as session:
        user = await session.execute(stmt)
        user = user.scalar()
        user.language = language
        await session.commit()

async def get_user_groups(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User)
            .options(selectinload(User.groups), selectinload(User.owned_groups))
            .where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return []
        all_groups = {g.id: g for g in user.groups + user.owned_groups}
        return list(all_groups.values())

async def get_subgroups(group_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Subgroup).where(Subgroup.group_id == group_id)
        )
        if not result:
            return []
        return result.scalars().all()

async def add_event(sg_id: int, name: str, timestamp, comment: str):
    async with AsyncSessionLocal() as session:
        event = Event(sg_id=sg_id, name=name, timestamp=timestamp, comment=comment)
        session.add(event)
        await session.commit()

from sqlalchemy.exc import SQLAlchemyError

async def create_new_event(sg_id: int, name: str, timestamp: str, comment: str):
    async with AsyncSessionLocal() as session:
        try:
            event = Event(sg_id=sg_id, name=name, timestamp=timestamp, comment=comment)
            session.add(event)
            await session.commit()
            print(f"DEBUG: Событие создано: sg_id={sg_id}, name={name}, timestamp={timestamp}, comment={comment}")
        except SQLAlchemyError as e:
            await session.rollback()
            print(f"ERROR: Не удалось создать событие: {e}")
            raise


async def get_events(subgroup_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Event).where(Event.sg_id == subgroup_id)
        )
        events = result.scalars().all()
        return [{"id": e.id, "name": e.name} for e in events]

async def get_event_info(id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Event).where(Event.id == id)
        )
        event = result.scalars().first()
        return event

async def get_group(group_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalars().first()
        return group

async def del_sg(sg_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                delete(Subgroup).where(Subgroup.sg_id == sg_id)
            )
        await session.commit()

async def del_group(group_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                delete(Group).where(Group.id == group_id)
            )
        await session.commit()

async def rename_group(group_id: int, new_name: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                update(Group).where(Group.id == group_id).values(name=new_name)
            )

async def rename_sg(sg_id: int, new_name: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                update(Subgroup).where(Subgroup.sg_id == sg_id).values(name=new_name)
            )