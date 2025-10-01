from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
from aiogram_dialog import setup_dialogs
from redis.asyncio import Redis

from aiodialog.dialogs.creategroup import create_dialog
from config.config import load_config, Config
from db.requests import engine
from db.tables import Base
from aiodialog.dialogs.start import start_dialog
from handlers.user import user_router


async def main():
    config: Config = load_config()
    redis = Redis(host="localhost", port=6379, db=0, decode_responses=True)
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(redis=redis)
    dp.include_router(user_router)

    dp.include_router(start_dialog)
    dp.include_router(create_dialog)
    setup_dialogs(dp)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await dp.start_polling(bot)

asyncio.run(main())