from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button
from aiogram.types import Message, CallbackQuery
from functools import partial
from aiodialog.StatsGroup import CreateSg, StartSg


async def back_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.back()

def name_check(text: str):
    if not len(text):
        raise ValueError("Название должно содержать хотя бы один символ")
    if len(text) > 50:
        raise ValueError(f"Максимальная длина названия - 50 символов")
    return text

async def correct_check(message: Message, widget: ManagedTextInput, manager: DialogManager, text: str, arg: str):
    manager.dialog_data[arg] = text
    await manager.next()

async def admins_check(text: str):
    admins = text.split()
    for admin_id in admins:
        if not admin_id.isdigit():
            raise ValueError("Кажется, вы ввели что-то кроме айди")
    return admins

async def failed_check(message: Message, widget: ManagedTextInput, manager: DialogManager, error: ValueError):
    await message.answer(f"{error}")

async def gap(message: Message, widget: ManagedTextInput, manager: DialogManager, text: str):
    await message.answer("Умница")
    await manager.start(StartSg.start)

create_dialog = Dialog(
    Window(
        Const("Придумайте название для группы"),
        TextInput(id="Name_input", type_factory=name_check,
                  on_success=lambda m, w, mgr, text: correct_check(m, w, mgr, text, "name"),
                  on_error=failed_check),
        state=CreateSg.name
    ),
    Window(Const(text="Теперь введите подгруппы в формате 'Subgroup 1, Subgroup 2, Subgroup 3'"),
           TextInput(id="Subgroups_input", type_factory=name_check,
                     on_success=lambda m, w, mgr, text: correct_check(m, w, mgr, text, "subgroups"),
                     on_error=failed_check),
           Button(text=Const("Назад"), id="Back_button", on_click=back_button),
           state=CreateSg.subgroups),
    Window(Const(text="Осталось ввести айди администраторов в формате '123456677 545444322', либо просто отправьте None"),
           TextInput(id="Admins_input", type_factory=name_check, on_success=gap, on_error=failed_check),
           Button(text=Const("Назад"), id="Back_button", on_click=back_button),
           state=CreateSg.admins),
)