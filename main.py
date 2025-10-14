from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio

from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from redis.asyncio import Redis

from aiodialog.dialogs.dialogs import create_dialog, start_dialog, groups_dialog, event_dialog, group_admin_dialog, \
    subgroups_admin_dialog, edit_event_dialog, join_dialog, solo_dialog
from config.config import load_config, Config
from db.requests import engine
from db.tables import Base
from handlers.user import user_router


async def main():
    config: Config = load_config()
    redis = Redis(host="localhost", port=6379, db=0, decode_responses=True)
    storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)
    dp.include_router(user_router)

    dp.include_router(start_dialog)
    dp.include_router(create_dialog)
    dp.include_router(groups_dialog)
    dp.include_router(event_dialog)
    dp.include_router(group_admin_dialog)
    dp.include_router(subgroups_admin_dialog)
    dp.include_router(edit_event_dialog)
    dp.include_router(join_dialog)
    dp.include_router(solo_dialog)
    setup_dialogs(dp)
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await dp.start_polling(bot)

asyncio.run(main())