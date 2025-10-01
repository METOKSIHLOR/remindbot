from aiogram import Router
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode
from aiogram.types import Message
from db.requests import create_user
from aiodialog.dialogs.start import StartSg

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message, dialog_manager: DialogManager):
    telegram_user = message.from_user

    telegram_id = telegram_user.id
    first_name = telegram_user.first_name
    last_name = telegram_user.last_name

    await create_user(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name
    )
    await dialog_manager.start(StartSg.start, mode=StartMode.RESET_STACK)
