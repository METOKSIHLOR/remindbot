import asyncio
import json
from datetime import datetime, timezone
from aiogram import Bot
from nats.aio.client import Client as NATS
from nats.errors import MsgAlreadyAckdError
from nats.js.errors import KeyNotFoundError, KeyDeletedError

from db.requests import get_event_info, get_group_users, get_group, remove_solo_reminder
from config.config import load_config

async def process_schedule(msg, bot, js):
    try:
        data = json.loads(msg.data.decode())
        event_id = data["event_id"]
        group_id = data["group_id"]
        notify_time = datetime.fromisoformat(data["notify_time"])

        if notify_time.tzinfo is None:
            notify_time = notify_time.replace(tzinfo=timezone.utc)

        delay = (notify_time - datetime.now(timezone.utc)).total_seconds()
        if delay <= 0:
            print(f"⏩ Připomenutí události {event_id} bylo přeskočeno")
            return

        kv = await js.key_value("notifications")
        key = f"event_{event_id}"

        await asyncio.sleep(delay)

        try:
            entry = await kv.get(key)
        except (KeyNotFoundError, KeyDeletedError):
            print(f"❌ Připomenutí {event_id} zrušeno nebo smazáno")
            return
        print("KV entry:", await kv.get(key))

        if not entry:
            print(f"❌ Připomenutí {event_id} zrušeno")
            return

        event = await get_event_info(event_id)
        group = await get_group(group_id)
        users = await get_group_users(group_id)
        print(await get_group_users(group_id))
        user_kv = await js.key_value("user_settings")

        for user in users:
            try:
                setting = await user_kv.get(f"user_{user.telegram_id}")
                if setting and json.loads(setting.value).get(f"group_{group_id}") is False:
                    continue
                await bot.send_message(user.telegram_id, f"🔔 Připomínám událost "
                                                         f"«{event.name}» ve skupině {group.name}!")
            except Exception as e:
                print(f"⚠️ Chyba při odesílání uživateli {user.telegram_id}: {e}")
    finally:
        try:
            await msg.ack()
        except MsgAlreadyAckdError:
            pass

async def process_solo_notify(msg, bot, js):
    try:
        data = json.loads(msg.data.decode())
        user_id = data["user_id"]
        text = data["text"]
        notify_time = datetime.fromisoformat(data["notify_time"])
        reminder_id = data["reminder_id"]

        if notify_time.tzinfo is None:
            notify_time = notify_time.replace(tzinfo=timezone.utc)

        delay = (notify_time - datetime.now(timezone.utc)).total_seconds()
        if delay <= 0:
            print(f"⏩ Připomenutí pro uživatele {reminder_id} bylo přeskočeno")
            return

        await asyncio.sleep(delay)

        kv = await js.key_value("notifications")
        key = f"solo_{user_id}_{reminder_id}"
        try:
            entry = await kv.get(key)
        except (KeyNotFoundError, KeyDeletedError):
            print(f"❌ Připomenutí {reminder_id} zrušeno")
            return

        await bot.send_message(user_id, f"🔔 Připomenutí: {text}")
        await kv.delete(key)
        await remove_solo_reminder(reminder_id)

    finally:
        try:
            await msg.ack()
        except MsgAlreadyAckdError:
            pass

async def main():
    config = load_config()
    bot = Bot(token=config.bot.token)

    nc = NATS()
    await nc.connect("nats://localhost:4222")
    js = nc.jetstream()

    async def schedule_cb(msg):
        asyncio.create_task(process_schedule(msg, bot, js))

    await js.subscribe(
        "events.schedule",
        durable="notify_worker",
        deliver_policy="all",
        cb=schedule_cb
    )

    async def solo_cb(msg):
        asyncio.create_task(process_solo_notify(msg, bot, js))

    await js.subscribe(
        "events.personal",
        durable="solo_worker",
        deliver_policy="all",
        cb=solo_cb
    )

    print("✅ Notification worker spuštěn")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
