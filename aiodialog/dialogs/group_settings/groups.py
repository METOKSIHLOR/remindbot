from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Select, Row, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format
from functools import partial
from db.requests import get_user_groups, get_subgroups
from aiodialog.StatsGroup import GroupsSg, StartSg
from aiodialog.dialogs.create_group.creategroup import back_button
async def main_menu(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(StartSg.main_menu)

async def groups_getter(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user.id
    page = dialog_manager.dialog_data.get("page", 0)

    groups = await get_user_groups(user)
    total = len(groups)

    start = page * 8
    end = start + 8
    page_groups = groups[start:end]

    return {
        "groups": page_groups,
        "page": page,
        "total": total,
    }

async def on_group_selected(c, w, manager: DialogManager, item_id):
    group_id = int(item_id)
    await manager.start(state=GroupsSg.my_subgroups, data={"group_id": group_id})

async def on_subgroup_selected(c, w, manager: DialogManager, item_id):
    print(f"Выбрана подгруппа {item_id}")

async def subgroups_getter(dialog_manager: DialogManager, **kwargs):
    group_id = dialog_manager.start_data.get("group_id")
    subgroups = await get_subgroups(group_id)
    return {"subgroups": subgroups}

subgroups_select = Select(
    Format("{item.name}"),
    id="subgroups_select",
    item_id_getter=lambda x: x.sg_id,
    items="subgroups",
    on_click=on_subgroup_selected,
)

subgroups_group = ScrollingGroup(
    subgroups_select,
    id="subgroups_group",
    width=1,
    height=5
)

groups_select = Select(
    Format("{item.name}"),
    id="group_select",
    item_id_getter=lambda g: g.id,
    items="groups",
    on_click=on_group_selected,
)

async def change_page(c, w, manager: DialogManager, delta: int):
    page = manager.dialog_data.get("page", 0)
    new_page = max(0, page + delta)
    manager.dialog_data["page"] = new_page
    await manager.show()

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