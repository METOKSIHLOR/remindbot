from aiogram import Router
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode
from aiogram.types import Message

from aiodialog.StatsGroup import StartSg
from db.requests import create_user, get_user

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message, dialog_manager: DialogManager):
    telegram_user = message.from_user
    telegram_id = telegram_user.id
    user = await get_user(telegram_id=telegram_id)
    if not user:
        first_name = telegram_user.first_name
        last_name = telegram_user.last_name

        await create_user(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name
        )
        await dialog_manager.start(StartSg.start)

    elif not user.language:
        await dialog_manager.reset_stack()
        await dialog_manager.start(StartSg.start)
    else:
        await dialog_manager.reset_stack()
        await dialog_manager.start(StartSg.main_menu)

@user_router.message(Command("change_language"))
async def cmd_change_language(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(StartSg.start)