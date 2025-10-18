from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from aiodialog.StatsGroup import CreateSg, GroupsSg, JoinSg, SoloSg
from aiogram_dialog.widgets.kbd import Button

async def cr_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.reset_stack()
    await manager.start(CreateSg.name)

async def jn_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.reset_stack()
    await manager.start(JoinSg.id)


async def sl_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.reset_stack()
    await manager.start(SoloSg.main)

async def groups_button(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.reset_stack()
    await manager.start(GroupsSg.my_groups)

