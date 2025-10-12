import json
from datetime import datetime
from nats.aio.client import Client as NATS
from nats.js.api import KeyValueConfig

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
    kv = await js.key_value("notifications")
    key = f"event_{event_id}"

    await kv.put(key, json.dumps({
        "notify_time": notify_time.isoformat(),
        "group_id": group_id,
    }).encode("utf-8"))

    await js.publish("events.schedule", json.dumps({
        "event_id": event_id,
        "notify_time": notify_time.isoformat(),
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