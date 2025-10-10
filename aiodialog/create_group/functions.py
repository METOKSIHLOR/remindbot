from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiodialog.StatsGroup import StartSg
from db.requests import create_group, create_subgroup
from aiogram_dialog.widgets.kbd import Button

async def back_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.back()

async def cancel_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.reset_stack()
    await manager.start(StartSg.main_menu)

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

