import asyncio
import json
from datetime import datetime
from aiogram import Bot
from nats.aio.client import Client as NATS
from db.requests import get_event_info, get_group_users
from config.config import load_config

async def process_schedule(msg, bot, js):
    data = json.loads(msg.data.decode())
    event_id = data["event_id"]
    group_id = data["group_id"]
    notify_time = datetime.fromisoformat(data["notify_time"])

    delay = (notify_time - datetime.now()).total_seconds()
    if delay <= 0:
        print(f"⏩ Пропущено уведомление event {event_id}")
        return

    kv = await js.key_value("notifications")
    key = f"event_{event_id}"

    await asyncio.sleep(delay)

    entry = await kv.get(key)
    print("KV entry:", await kv.get(key))

    if not entry:
        print(f"❌ Напоминание {event_id} отменено")
        return

    event = await get_event_info(event_id)
    users = await get_group_users(group_id)
    print(await get_group_users(group_id))
    user_kv = await js.key_value("user_settings")

    for user in users:
        try:
            setting = await user_kv.get(f"user_{user.telegram_id}")
            if setting and json.loads(setting.value).get(f"group_{group_id}") is False:
                continue
            await bot.send_message(user.telegram_id, f"🔔 Напоминание: завтра событие «{event.name}»!")
        except Exception as e:
            print(f"⚠️ Ошибка отправки пользователю {user.telegram_id}: {e}")


async def main():
    config = load_config()
    bot = Bot(token=config.bot.token)

    nc = NATS()
    await nc.connect("nats://localhost:4222")
    js = nc.jetstream()

    async def schedule_cb(msg):
        await process_schedule(msg, bot, js)

    await js.subscribe(
        "events.schedule",
        durable="notification_worker",
        cb=schedule_cb
    )
    print("✅ Notification worker запущен")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())