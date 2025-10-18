from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from aiodialog.group_settings.group_functions import on_group_selected
from aiodialog.StatsGroup import StartSg

async def main_menu(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(StartSg.main_menu)

groups_select = Select(
    Format("{item.name}"),
    id="group_select",
    item_id_getter=lambda g: g.id,
    items="result",
    on_click=on_group_selected,
)

groups_group = ScrollingGroup(
    groups_select,
    id="groups_group",
    width=1,
    height=5
)
