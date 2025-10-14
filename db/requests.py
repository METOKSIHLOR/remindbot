from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, selectinload
from db.tables import User, Group, Subgroup, Event, JoinRequest, user_group_association, SoloReminder
from config.config import load_config
from sqlalchemy import select, delete, update, exists, and_
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

async def get_sg(sg_id: int):
    async with AsyncSessionLocal() as session:
        subgroup = await session.execute(select(Subgroup).where(Subgroup.sg_id == sg_id))
        return subgroup.scalar_one_or_none()


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


async def create_new_event(sg_id: int, name: str, timestamp: datetime, comment: str, notify: int):
    timestamp_utc = timestamp.astimezone(timezone.utc)

    async with AsyncSessionLocal() as session:
        event = Event(
            sg_id=sg_id,
            name=name,
            timestamp=timestamp_utc.replace(tzinfo=None),
            comment=comment
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)

    notify_time_utc = timestamp_utc - timedelta(hours=notify)

    nc, js = await get_js_connection()
    subgroup = await get_sg(sg_id)
    await schedule_event_notify(js, event.id, notify_time_utc, group_id=subgroup.group_id)

    print("Now (UTC):", datetime.now(timezone.utc))
    print("Notify time (UTC):", notify_time_utc)
    print("Delay (sec):", (notify_time_utc - datetime.now(timezone.utc)).total_seconds())

    await nc.close()
    return event

async def get_events(subgroup_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Event).where(Event.sg_id == subgroup_id)
        )
        events = result.scalars().all()
        tz = timezone(timedelta(hours=2))

        processed = []
        for e in events:
            ts = e.timestamp
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            ts = ts.astimezone(tz)
            processed.append({
                "id": e.id,
                "name": e.name,
                "timestamp": ts.strftime("%H:%M %d.%m.%Y")
            })

        return processed

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

async def edit_time_event(event_id: int, new_time: datetime, notify: int):
    timestamp_utc = new_time.astimezone(timezone.utc).replace(tzinfo=None)
    notify_time_utc = timestamp_utc - timedelta(hours=notify)

    event_id = int(event_id)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await session.execute(
                update(Event)
                .where(Event.id == event_id).values(timestamp=timestamp_utc)
            )

    nc, js = await get_js_connection()
    event = await get_event_info(event_id)
    subgroup = await get_sg(event.sg_id)
    await cancel_event_notify(js, event_id)
    await schedule_event_notify(js, event.id, notify_time_utc, group_id=subgroup.group_id)

    print("Now (UTC):", datetime.now(timezone.utc))
    print("Notify time (UTC):", notify_time_utc)

    # ===== Вставка исправления =====
    if notify_time_utc.tzinfo is None:
        notify_time_utc = notify_time_utc.replace(tzinfo=timezone.utc)

    delay_seconds = (notify_time_utc - datetime.now(timezone.utc)).total_seconds()
    print("Delay (sec):", delay_seconds)
    # ================================

    await nc.close()
    return event


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

async def remove_user_from_group(user_id: int, group_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(user_group_association).where(
                and_(
                    user_group_association.c.user_id == user_id,
                    user_group_association.c.group_id == group_id
                )
            )
        )
        print(user_id, group_id)
        await session.commit()

async def add_solo_reminder(user_id: int, name: str, notify_time: datetime) -> int:
    async with AsyncSessionLocal() as session:
        reminder = SoloReminder(user_id=user_id, name=name, notify_time=notify_time)
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)
        return reminder.id

async def get_solo_reminders(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SoloReminder).where(SoloReminder.user_id == user_id)
        )
        return result.scalars().all()

async def remove_solo_reminder(reminder_id: int):
    async with AsyncSessionLocal() as session:
        await session.execute(delete(SoloReminder).where(SoloReminder.id == reminder_id))
        await session.commit()
