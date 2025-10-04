from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button
from aiogram.types import Message, CallbackQuery
from aiodialog.StatsGroup import CreateSg, StartSg
from db.requests import create_group, create_subgroup
from functools import partial

async def back_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.back()

def name_check(text: str):
    if not len(text):
        raise ValueError("Название должно содержать хотя бы один символ")
    if len(text) > 50:
        raise ValueError(f"Максимальная длина названия - 50 символов")
    return text

async def correct_check(message: Message, widget: ManagedTextInput, manager: DialogManager, result: str):
    manager.dialog_data["group_name"] = result
    await manager.next()

async def failed_check(message: Message, widget: ManagedTextInput, manager: DialogManager, error: ValueError):
    await message.answer(f"{error}")

def subgroups_check(text: str):
    subgroups = [s.strip() for s in text.split(",")]
    if not all(subgroups):
        raise ValueError("Неверный формат подгрупп")
    return subgroups

async def finish_create(message: Message, widget: ManagedTextInput, manager: DialogManager, result: list):
    manager.dialog_data["subgroup_names"] = result
    group = await create_group(name=manager.dialog_data["group_name"], owned_by=message.from_user.id)
    for subgroup_name in manager.dialog_data["subgroup_names"]:
        await create_subgroup(name=subgroup_name, group_id=group.id)
    await message.answer(f"Поздравляю! Группа {group.name} была успешно создана!")
    manager.dialog_data.pop("group_name", None)
    manager.dialog_data.pop("subgroup_names", None)
    await manager.start(state=StartSg.main_menu)


create_dialog = Dialog(
    Window(
        Const("Придумайте название для группы"),
        TextInput(id="Name_input", type_factory=name_check,
                  on_success=correct_check,
                  on_error=failed_check),
        state=CreateSg.name
    ),
    Window(Const(text="Теперь введите подгруппы в формате 'Subgroup 1, Subgroup 2, Subgroup 3'"),
           TextInput(id="Subgroups_input", type_factory=subgroups_check,
                     on_success=finish_create,
                     on_error=failed_check),
           Button(text=Const("Назад"), id="back_button", on_click=back_button),
           state=CreateSg.subgroups),
)
