from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.text import Const, Format
from functools import partial

from aiodialog.group_settings.group_functions import on_group_selected, change_page
from aiodialog.StatsGroup import StartSg

async def main_menu(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(StartSg.main_menu)

groups_select = Select(
    Format("{item.name}"),
    id="group_select",
    item_id_getter=lambda g: g.id,
    items="groups",
    on_click=on_group_selected,
)

next_button = Button(Const(text="Вперед"), id="next_button", on_click=partial(change_page, delta=+1))
prev_button = Button(Const(text="Назад"), id="prev_button", on_click=partial(change_page, delta=-1))
