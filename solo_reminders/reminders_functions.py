from datetime import datetime, timezone, timedelta

from aiogram_dialog import DialogManager

import json

from nats.js.errors import KeyNotFoundError, KeyDeletedError

from aiodialog.StatsGroup import SoloSg
from db.requests import add_solo_reminder, get_solo_reminders, remove_solo_reminder
from nats_js.notifications import get_js_connection


async def add_notify_button(c, w, manager: DialogManager):
    await manager.switch_to(SoloSg.add_name)

async def solo_name_success(c, w, manager: DialogManager, result: str):
    state = manager.middleware_data["state"]
    await state.update_data({"solo_name": result})
    await manager.next()

async def create_solo_notify(c, w, manager: DialogManager, notify_time: datetime):
    state = manager.middleware_data["state"]
    data = await state.get_data()

    user_id = manager.event.from_user.id
    name = data.get("solo_name")

    try:
        tz_utc_plus_2 = timezone(timedelta(hours=2))
        if notify_time.tzinfo is None:
            notify_time = notify_time.replace(tzinfo=tz_utc_plus_2)

        now = datetime.now(tz=tz_utc_plus_2)
        if notify_time <= now:
            await c.answer("❌ Время не может быть в прошлом. Попробуйте ещё раз.")
            return
    except ValueError:
        await c.answer("❌ Неверный формат даты. Используйте 'ДД.ММ.ГГГГ ЧЧ:ММ'.")
        return

    naive_time = notify_time.replace(tzinfo=None)
    reminder_id = await add_solo_reminder(user_id=user_id, name=name, notify_time=naive_time)

    nc, js = await get_js_connection()
    kv = await js.key_value("notifications")
    key = f"solo_{user_id}_{reminder_id}"
    await kv.put(key, json.dumps({
        "user_id": user_id,
        "text": name,
        "notify_time": notify_time.isoformat(),
        "reminder_id": reminder_id
    }).encode("utf-8"))

    await js.publish("events.personal", json.dumps({
        "user_id": user_id,
        "text": name,
        "notify_time": notify_time.isoformat(),
        "reminder_id": reminder_id
    }).encode())

    await c.answer(f"✅ Напоминание '{name}' установлено на {notify_time.strftime('%d.%m.%Y %H:%M')}")
    await manager.reset_stack()
    await manager.start(SoloSg.main)

async def del_solo_button(c, w, manager: DialogManager):
    await manager.switch_to(SoloSg.del_notify)

async def cancel_solo_notify(js, reminder_id: int, user_id: int):
    kv = await js.key_value("notifications")
    key = f"solo_{user_id}_{reminder_id}"
    try:
        await kv.delete(key)
    except (KeyNotFoundError, KeyDeletedError):
        pass

    await remove_solo_reminder(reminder_id)

async def notify_getter(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    notifies = await get_solo_reminders(user_id=user_id)

    result = []
    for notify in notifies:
        result.append({
            "id": notify.id,
            "user_id": user_id,
            "name": notify.name,
            "notify_time": notify.notify_time.isoformat(),
        })

    return {"result": result}

async def del_notify_user_selected(c, w, manager: DialogManager, item_id: int):
    user_id = manager.event.from_user.id
    nc, js = await get_js_connection()
    await cancel_solo_notify(js, reminder_id=int(item_id), user_id=user_id)

    await manager.update(data={})