from aiogram_dialog import DialogManager
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

def event_time_check(text: str):
    return text

async def event_time_success(message: Message, widget: ManagedTextInput, manager: DialogManager, result: str):
    manager.dialog_data["event_time"] = result
    await manager.next()

async def event_time_fail(message: Message, widget: ManagedTextInput, manager: DialogManager, error: ValueError):
    pass

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

    if not sg_id:
        await message.answer("Ошибка: не удалось определить подгруппу!")
        return

    name = manager.dialog_data["event_name"]
    timestamp = manager.dialog_data["event_time"]
    comment = result

    await create_new_event(sg_id=sg_id, name=name, timestamp=timestamp, comment=comment)
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