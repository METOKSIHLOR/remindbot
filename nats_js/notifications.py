import json
from datetime import datetime
from zoneinfo import ZoneInfo

from nats.aio.client import Client as NATS
from nats.js.api import KeyValueConfig
from nats.js.kv import KeyValue


async def get_js_connection():
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    js = nc.jetstream()

    try:
        stream = await js.stream_info("EVENTS")
    except Exception:
        await js.add_stream(
            name="EVENTS",
            subjects=["events.*"],
        )
        print("✅ JetStream stream 'EVENTS' created")

    try:
        await js.create_key_value(KeyValueConfig(bucket="notifications"))
    except Exception:
        pass
    try:
        await js.create_key_value(KeyValueConfig(bucket="user_settings"))
    except Exception:
        pass

    return nc, js

async def schedule_event_notify(js, event_id: int, notify_time: datetime, group_id: int):
    prague_tz = ZoneInfo("Europe/Prague")

    if notify_time.tzinfo is None:
        notify_time = notify_time.replace(tzinfo=prague_tz)

    kv = await js.key_value("notifications")
    key = f"event_{event_id}"

    prague_time = notify_time.astimezone(prague_tz)

    await kv.put(key, json.dumps({
        "notify_time": prague_time.isoformat(),
        "group_id": group_id,
    }).encode("utf-8"))

    await js.publish("events.schedule", json.dumps({
        "event_id": event_id,
        "notify_time": prague_time.isoformat(),
        "group_id": group_id,
    }).encode())


async def cancel_event_notify(js, event_id: int):
    kv = await js.key_value("notifications")
    await kv.delete(f"event_{event_id}")
    await js.publish("events.cancel", json.dumps({"event_id": event_id}).encode())


async def set_user_group_notify(js, user_id: int, group_id: int, enabled: bool):
    kv = await js.key_value("user_settings")
    key = f"user_{user_id}"

    try:
        current = json.loads((await kv.get(key)).value)
    except Exception:
        current = {}

    current[f"group_{group_id}"] = enabled
    await kv.put(key, json.dumps(current).encode("utf-8"))

async def schedule_solo_notify(js, user_id: int, reminder_id: int, text: str, notify_time: datetime):
    key = f"solo_{user_id}_{reminder_id}"
    payload = {
        "user_id": user_id,
        "text": text,
        "notify_time": notify_time.isoformat(),
        "reminder_id": reminder_id
    }
    await js.put(key, json.dumps(payload).encode())
    await js.publish("events.personal", json.dumps(payload).encode())

async def cancel_solo_notify(js, user_id: int, reminder_id: int):
    key = f"solo_{user_id}_{reminder_id}"
    await js.delete(key)
    await js.publish("events.personal.cancel", json.dumps({
        "user_id": user_id,
        "reminder_id": reminder_id
    }).encode())