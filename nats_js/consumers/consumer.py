import asyncio
from asyncio import CancelledError
from datetime import datetime, timedelta, timezone
import json
import nats
from aiogram import Bot

from config.config import load_config
from nats.aio.msg import Msg

config = load_config()
bot = Bot(token=config.bot.token)

async def main():
    nc = await nats.connect("nats://127.0.0.1:4222")
    js = nc.jetstream()
    subject = "aiogram.delayed.messages"
    stream = 'delayed_messages_aiogram'
    sub = await js.subscribe(
        subject=subject,
        stream=stream,
        durable='delayed_messages_consumer',
        manual_ack=True
    )
    async for msg in sub.messages:
        data = json.loads(msg.data.decode())
        chat_id = data["chat_id"]
        text = data["text"]
        send_at = datetime.fromisoformat(data["send_at"]).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delay = (send_at - now).total_seconds()

        if delay > 0:
            await asyncio.sleep(delay)

        try:
            await bot.send_message(chat_id, text)
            await msg.ack()
        except Exception as e:
            print("Ошибка при отправке:", e)
            await msg.nak()


asyncio.run(main())