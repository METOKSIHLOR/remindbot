import asyncio
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import Bot
from nats.aio.client import Client as NATS
from nats.errors import MsgAlreadyAckdError
from nats.js.errors import KeyNotFoundError, KeyDeletedError

from db.requests import get_event_info, get_group_users, get_group, remove_solo_reminder, get_sg
from config.config import load_config

active_event_tasks: dict[int, asyncio.Task] = {}


async def process_schedule(msg, bot, js):
    prague_tz = ZoneInfo("Europe/Prague")
    data = json.loads(msg.data.decode())
    event_id = data["event_id"]

    kv = await js.key_value("notifications")
    try:
        entry = await kv.get(f"event_{event_id}")
    except (KeyNotFoundError, KeyDeletedError):
        print(f"❌ Připomenutí {event_id} zrušeno")
        await safe_ack(msg)
        return

    notify_time = datetime.fromisoformat(json.loads(entry.value)['notify_time'])
    if notify_time.tzinfo is None:
        notify_time = notify_time.replace(tzinfo=prague_tz)

    delay = (notify_time - datetime.now(prague_tz)).total_seconds()
    if delay <= 0:
        print(f"⏩ Připomenutí události {event_id} bylo přeskočeno")
        await safe_ack(msg)
        return

    # ✅ подтверждаем сообщение сразу, дальше таска уже не будет повторно ack
    await safe_ack(msg)

    async def sleep_and_notify():
        try:
            await asyncio.sleep(delay)
            entry_now = await kv.get(f"event_{event_id}")
            notify_time_now = datetime.fromisoformat(json.loads(entry_now.value)['notify_time'])
            if notify_time_now.tzinfo is None:
                notify_time_now = notify_time_now.replace(tzinfo=prague_tz)

            if datetime.now(prague_tz) < notify_time_now:
                print(f"❌ Старое уведомление {event_id}, пропускаем")
                return

            event = await get_event_info(event_id)
            subgroup = await get_sg(event.sg_id)
            group = await get_group(subgroup.group_id)
            users = await get_group_users(subgroup.group_id)
            user_kv = await js.key_value("user_settings")
            for user in users:
                setting = await user_kv.get(f"user_{user.telegram_id}")
                if setting and not json.loads(setting.value).get(f"group_{subgroup.group_id}", True):
                    continue
                await bot.send_message(user.telegram_id, f"🔔 Připomínám událost «{event.name}» ({subgroup.name}) ve skupině {group.name}")
        except asyncio.CancelledError:
            print(f"❌ Задача уведомления {event_id} отменена")
            return

    if event_id in active_event_tasks:
        active_event_tasks[event_id].cancel()

    task = asyncio.create_task(sleep_and_notify())
    active_event_tasks[event_id] = task

async def safe_ack(msg):
    try:
        await msg.ack()
    except MsgAlreadyAckdError:
        pass



async def process_solo_notify(msg, bot, js):
    prague_tz = ZoneInfo("Europe/Prague")
    try:
        data = json.loads(msg.data.decode())
        user_id = data["user_id"]
        text = data["text"]
        notify_time = datetime.fromisoformat(data["notify_time"])
        reminder_id = data["reminder_id"]

        if notify_time.tzinfo is None:
            notify_time = notify_time.replace(tzinfo=prague_tz)

        delay = (notify_time - datetime.now(prague_tz)).total_seconds()
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
