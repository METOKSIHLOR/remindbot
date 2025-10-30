from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from aiogram_dialog import DialogManager, manager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram.types import Message

from aiodialog.StatsGroup import EventsSg, GroupsSg, StartSg
from db.requests import create_new_event, get_events, get_event_info
from db.tables import Event



def event_name_check(text: str):
    if not len(text) or len(text) > 100:
        raise ValueError("Název musí obsahovat 1 až 100 znaků.")
    return text

async def event_name_success(message: Message, widget: ManagedTextInput, manager: DialogManager, result: str):
    manager.dialog_data["event_name"] = result
    await manager.next()

async def event_name_fail(message: Message, widget: ManagedTextInput, manager: DialogManager, error: ValueError):
    await message.answer(f"{error}")

def parse_event_time(text: str):
    try:
        prague_tz = ZoneInfo("Europe/Prague")
        dt = datetime.strptime(text.strip(), "%H:%M %d.%m.%Y")
        dt = dt.replace(tzinfo=prague_tz)
        now_prague = datetime.now(prague_tz)
        if dt < now_prague:
            return None
        return dt
    except ValueError:
        return None

def time_type_factory(text: str) -> datetime:
    dt = parse_event_time(text)
    if not dt:
        raise ValueError("❌ Nesprávný formát času.")
    return dt

async def event_time_success(message: Message, widget: ManagedTextInput, manager: DialogManager, result: datetime):
    state = manager.middleware_data["state"]

    prague_tz = ZoneInfo("Europe/Prague")
    if result.tzinfo is None:
        result = result.replace(tzinfo=prague_tz)
    else:
        result = result.astimezone(prague_tz)

    await state.update_data(event_time=result.isoformat())
    await manager.next()

def comment_check(text: str):
    if len(text) > 2000:
        raise ValueError("Délka komentáře nesmí překročit 2000 znaků.")
    return text

async def event_comment_fail(message: Message, widget: ManagedTextInput, manager: DialogManager, error: ValueError):
    await message.answer(f"{error}")

async def event_comment_success(message: Message, widget: ManagedTextInput,
                                manager: DialogManager, result: str):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    sg_id = data.get("sg_now")
    notify = data.get("notify_time")
    if not sg_id:
        await message.answer("Chyba: Nepodařilo se určit podskupinu!")
        return

    event_time_utc = parse_event_time_utc(data["event_time"])
    now_utc = datetime.now(timezone.utc)
    notify_time_utc = event_time_utc - timedelta(hours=notify)

    if notify_time_utc < now_utc:
        print(f"notify_time: {notify_time_utc}, now: {now_utc}, event_time: {event_time_utc}")
        await message.answer(
            "❌ Připomenutí nelze nastavit do minulosti."
        )
        await manager.start(EventsSg.time)
        return

    name = manager.dialog_data["event_name"]
    timestamp_str = data.get("event_time")
    if isinstance(timestamp_str, datetime):
        timestamp = timestamp_str
    else:
        timestamp = datetime.fromisoformat(timestamp_str)
    comment = result

    event = await create_new_event(sg_id=sg_id, name=name, timestamp=timestamp, comment=comment, notify=notify)
    await manager.start(GroupsSg.my_events)


async def start_add_event(c, w, manager: DialogManager):
    await manager.start(EventsSg.name)

async def event_getter(dialog_manager: DialogManager, **kwargs):
    state = dialog_manager.middleware_data["state"]
    data = await state.get_data()
    sg_id = data.get("sg_now")
    print("DEBUG event_getter sg_id:", sg_id)

    if not sg_id:
        return {"events": []}
    events = await get_events(sg_id)
    is_admin = data.get("is_admin")
    return {"result": events, "is_admin": is_admin}

async def event_info_getter(dialog_manager: DialogManager, **kwargs):
    state = dialog_manager.middleware_data["state"]
    data = await state.get_data()
    event_now = data.get("event_now")
    print("DEBUG event__info_getter event_now:", event_now)
    event = await get_event_info(event_now)
    return {"result": event}


async def on_event_selected(c, w, manager: DialogManager, item_id):
    event_now = int(item_id)
    state = manager.middleware_data["state"]
    await state.update_data(event_now=event_now)
    await manager.start(GroupsSg.select_event)

def notify_check(text: str):
    if not text.isdigit():
        raise ValueError("Zdá se, že jste zadali něco jiného než počet hodin.")
    return int(text)


def parse_event_time_utc(text: str) -> datetime:
    prague_tz = ZoneInfo("Europe/Prague")

    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=prague_tz)
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc
    except ValueError:
        naive = datetime.strptime(text.strip(), "%H:%M %d.%m.%Y")
        dt = naive.replace(tzinfo=prague_tz)
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc

async def notify_success(c, w, manager: DialogManager, result: int):
    state = manager.middleware_data["state"]
    data = await state.get_data()

    """event_time_utc = parse_event_time_utc(data["event_time"])
    now_utc = datetime.now(timezone.utc)
    notify_time_utc = event_time_utc - timedelta(hours=result)

    if notify_time_utc < now_utc:
        print(f"notify_time: {notify_time_utc}, now: {now_utc}, event_time: {event_time_utc}")
        await c.answer(
            "❌ Připomenutí nelze nastavit do minulosti.\n"
            "Zadejte menší počet hodin."
        )
        return"""

    await state.update_data(notify_time=result)
    await manager.next()