from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Select, Row, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format
from functools import partial

from aiodialog.dialogs.group_settings.functions import on_group_selected, change_page, groups_getter
from aiodialog.dialogs.subgroup_settings.functions import subgroups_getter
from aiodialog.dialogs.subgroup_settings.subgroups import subgroups_group
from aiodialog.StatsGroup import GroupsSg, StartSg
from aiodialog.dialogs.create_group.creategroup import back_button

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
groups_dialog = Dialog(
    Window(
        Const(text="Ваши группы:"),
        groups_select,
        Row(prev_button, next_button),
        Button(text=Const("Главное меню"), id="main_menu", on_click=main_menu),
        state=GroupsSg.my_groups,
        getter=groups_getter,),
    Window(
        Const(text="Ваши подгруппы:"),
        subgroups_group,
        Button(text=Const("Группы"), id="back", on_click=back_button),
        Button(text=Const("Главное меню"), id="main_menu", on_click=main_menu),
        state=GroupsSg.my_subgroups,
        getter=subgroups_getter,
    )
)