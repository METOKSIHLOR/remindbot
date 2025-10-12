from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, selectinload
from db.tables import User, Group, Subgroup, Event, JoinRequest, user_group_association
from config.config import load_config
from sqlalchemy import select, delete, update, exists
import asyncio

from nats_js.notifications import get_js_connection, schedule_event_notify, cancel_event_notify, set_user_group_notify

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
        await session.refresh(group)

        await session.execute(
            user_group_association.insert().values(
                user_id=owned_by,
                group_id=group.id
            )
        )
        await session.commit()
        nc, js = await get_js_connection()
        await set_user_group_notify(js, user_id=owned_by, group_id=group.id, enabled=True)
        await nc.close()

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


async def create_new_event(sg_id: int, name: str, timestamp: datetime, comment: str):
    async with AsyncSessionLocal() as session:
        event = Event(sg_id=sg_id, name=name, timestamp=timestamp, comment=comment)
        session.add(event)
        await session.commit()
        await session.refresh(event)
    nc, js = await get_js_connection()
    notify_time = datetime.now(timezone.utc) + timedelta(seconds=10)
    await schedule_event_notify(js, event.id, notify_time, group_id=sg_id)
    await nc.close()

    return event


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
        result = await session.execute(
            select(Group)
            .where(Group.id == group_id)
            .options(
                selectinload(Group.join_requests),
                selectinload(Group.members),
                selectinload(Group.subgroups).selectinload(Subgroup.events)
            )
        )
        group = result.scalar_one_or_none()

        if not group:
            return False

        for jr in group.join_requests:
            if jr.user_id is None:
                await session.delete(jr)

        await session.delete(group)
        await session.commit()
        return True

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

async def rename_event(event_id: int, new_name: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                update(Event)
                .where(Event.id == event_id)
                .values(name=new_name)
            )
        await session.commit()

async def delete_event(event_id: int):
    async with AsyncSessionLocal() as session:
        event = await session.get(Event, event_id)
        if event:
            await session.delete(event)
            await session.commit()

    nc, js = await get_js_connection()
    await cancel_event_notify(js, event_id)
    await nc.close()

async def edit_time_event(event_id: int, new_time: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                update(Event)
                .where(Event.id == int(event_id)).values(timestamp=new_time)
            )

async def edit_comment_event(event_id: int, new_comment: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                update(Event)
                .where(Event.id == int(event_id)).values(comment=new_comment)
            )


async def create_join_request(user_id: int, group_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            join_request = JoinRequest(user_id=int(user_id), group_id=int(group_id))
            session.add(join_request)
        await session.commit()

async def add_user_group(group_id: int, user_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = await session.get(User, user_id)
            group = await session.execute(
                select(Group)
                .options(selectinload(Group.members))
                .where(Group.id == group_id)
            )
            group = group.scalar_one()
            group.members.append(user)
        await session.commit()

    nc, js = await get_js_connection()
    await set_user_group_notify(js, user_id=user_id, group_id=group_id, enabled=True)
    await nc.close()

async def get_joins(group_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(JoinRequest).options(selectinload(JoinRequest.user)).where(JoinRequest.group_id == group_id)
            )
            result = result.scalars().all()
        return result

async def get_one_join(id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(JoinRequest).options(selectinload(JoinRequest.user)).where(JoinRequest.id == id)
            )
        return result.scalars().first()

async def delete_join(id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                delete(JoinRequest).where(JoinRequest.id == id)
            )

async def exist_join(user_id: int, group_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            existing = await session.execute(
                select(JoinRequest)
                .where(JoinRequest.user_id == user_id)
                .where(JoinRequest.group_id == group_id)
            )
            existing_request = existing.scalars().first()

            if existing_request:
                return True
            return False

async def user_in_group(user_id: int, group_id: int):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = await session.execute(
                select(Group).where(
                    Group.id == group_id,
                    Group.members.any(User.telegram_id == user_id)
                )
            )
        return result.scalar().one_or_none() is not None

async def get_group_users(group_id: int):
    async with AsyncSessionLocal() as session:
        query = (
            select(User)
            .join(user_group_association, User.telegram_id == user_group_association.c.user_id)
            .join(Group, Group.id == user_group_association.c.group_id)
            .where(Group.id == group_id)
        )

        result = await session.execute(query)
        users = result.scalars().all()
        return users