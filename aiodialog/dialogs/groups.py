from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Select, Row
from aiogram_dialog.widgets.text import Const, Format
from functools import partial
from aiodialog.dialogs.creategroup import back_button
from db.requests import get_user_groups
from aiodialog.StatsGroup import GroupsSg
import asyncio
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

async def on_group_selected(c, w, m, item_id):
    print(f"Выбрана группа {item_id}")

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
    await manager.reload()

next_button = Button(Const(text="Вперед"), id="next_button", on_click=partial(change_page, delta=+1))
prev_button = Button(Const(text="Назад"), id="prev_button", on_click=partial(change_page, delta=-1))
groups_dialog = Dialog(
    Window(
        Const(text="Ваши группы:"),
        groups_select,
        Row(prev_button, next_button),
        state=GroupsSg.my_groups,
        getter=groups_getter,
    )
)