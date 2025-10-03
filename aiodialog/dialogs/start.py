from random import randint

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button, Row
from db.requests import set_user_language

from db.requests import create_group
from aiodialog.StatsGroup import StartSg, CreateSg
from functools import partial

async def set_lang(callback: CallbackQuery, button: Button, manager: DialogManager, lang: str):
    await callback.answer(f"Язык выбран: {lang}")
    await set_user_language(callback.from_user.id, lang)
    await manager.next()

async def cr_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(CreateSg.name)

async def jn_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass

async def sl_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass

async def groups_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


start_dialog = Dialog(
    Window(
        Const("Please choose your native language."),
        Button(text=Const("Русский язык"), id="button_ru", on_click=partial(set_lang, lang="ru")),
        Button(text=Const("English"), id="button_en", on_click=partial(set_lang, lang="en")),
        Button(text=Const("Český jazyk"),id="button_cz", on_click=partial(set_lang, lang="cz")),
        state=StartSg.start),
    Window(
        Const("Выберите действие:"),
        Row(
            Button(text=Const("Мои группы"), id="my_groups", on_click=groups_button),
        ),
        Row(
            Button(text=Const("Создать группу"), id="create_button", on_click=cr_button),
            Button(text=Const("Вступить в группу"), id="join_button", on_click=jn_button),
        ),
        Button(text=Const("Одиночные напоминания"), id="solo_button", on_click=sl_button),
        state=StartSg.main_menu),
)
