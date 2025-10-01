import asyncio
from datetime import datetime

import nats


async def main():
    nc = await nats.connect("nats://127.0.0.1:4222")

    delay = 5

    message = 'Hello from Python-publisher!'

    headers = {
        'Tg-Delayed-Msg-Timestamp': str(datetime.now().timestamp()),
        'Tg-Delayed-Msg-Delay': str(delay)
    }
    subject = 'aiogram.delayed.messages'

    await nc.publish(subject, message.encode(encoding='utf-8'), headers=headers)

    print(f"Message '{message}' with headers {headers} published in subject `{subject}`")

    await nc.close()


asyncio.run(main())