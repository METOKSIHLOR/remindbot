from datetime import datetime, timezone, timedelta

from aiogram_dialog import DialogManager, manager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram.types import Message

from aiodialog.StatsGroup import EventsSg, GroupsSg, StartSg
from db.requests import create_new_event, get_events, get_event_info
from db.tables import Event



def event_name_check(text: str):
    if not len(text) or len(text) > 100:
        raise ValueError("Название должно содержать от 1 до 100 символов.")
    return text

async def event_name_success(message: Message, widget: ManagedTextInput, manager: DialogManager, result: str):
    manager.dialog_data["event_name"] = result
    await manager.next()

async def event_name_fail(message: Message, widget: ManagedTextInput, manager: DialogManager, error: ValueError):
    await message.answer(f"{error}")

def parse_event_time(text: str):
    try:
        dt = datetime.strptime(text.strip(), "%d.%m.%Y %H:%M")
        dt = dt.replace(tzinfo=timezone(timedelta(hours=2)))
        if dt < datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=2))):
            return None
        return dt
    except ValueError:
        return None

def time_type_factory(text: str) -> datetime:
    dt = parse_event_time(text)
    if not dt:
        raise ValueError("Неверный формат времени.")
    return dt

async def event_time_success(message: Message, widget: ManagedTextInput, manager: DialogManager, result: datetime):
    state = manager.middleware_data["state"]
    tz_utc_plus_2 = timezone(timedelta(hours=2))
    result = result.replace(tzinfo=tz_utc_plus_2)
    await state.update_data(event_time=result.isoformat())
    await manager.next()

def comment_check(text: str):
    if len(text) > 2000:
        raise ValueError("Длина комментария должна быть не больше 2000 символов.")
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
        await message.answer("Ошибка: не удалось определить подгруппу!")
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
        raise ValueError("Похоже, вы ввели что-то кроме количества часов.")
    return int(text)

def parse_event_time_mixed(date_str: str) -> datetime:
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return datetime.strptime(date_str, "%d.%m.%Y %H:%M")

async def notify_success(c, w, manager: DialogManager, result: int):
    state = manager.middleware_data["state"]
    data = await state.get_data()

    event_time = parse_event_time_mixed(data["event_time"])
    tz_utc_plus_2 = timezone(timedelta(hours=2))
    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=tz_utc_plus_2)

    now_utc = datetime.now(timezone.utc)
    event_time_utc = event_time.astimezone(timezone.utc)
    notify_time_utc = event_time_utc - timedelta(hours=result)

    if notify_time_utc <= now_utc:
        hours_until_event = (event_time_utc - now_utc).total_seconds() / 3600
        await c.answer(
            f"❌ Напоминание не может быть установлено в прошлое.\n"
            f"До события осталось примерно {hours_until_event:.1f} ч.\n"
            f"Введите меньшее количество часов."
        )
        return
    else:
        await state.update_data(notify_time=result)
        await manager.next()