from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from aiodialog.admin.event_admin_func import admin_rename_event_selected, admin_delete_event_selected
from aiodialog.admin.group_admin_func import admin_subgroup_selected, admin_rn_sg_selected

admin_sg_select = Select(
    Format("{item.name}"),
    id="subgroup_select",
    item_id_getter=lambda g: g.sg_id,
    items="result",
    on_click=admin_subgroup_selected,
)

admin_sg_group = ScrollingGroup(
    admin_sg_select,
    id="admin_sg_group",
    width=1,
    height=5
)

admin_rename_sg_select = Select(
    Format("{item.name}"),
    id="subgroup_rename_select",
    item_id_getter=lambda g: g.sg_id,
    items="result",
    on_click=admin_rn_sg_selected,
)

admin_rn_sg_group = ScrollingGroup(
    admin_rename_sg_select,
    id="admin_del_sg_group",
    width=1,
    height=5
)

admin_delete_select = Select(
    Format("{item[name]}"),
    id="delete_select",
    item_id_getter=lambda g: g["id"],
    items="result",
    on_click=admin_delete_event_selected,
)

admin_delete_group = ScrollingGroup(
    admin_delete_select,
    id="admin_delete_group",
    width=1,
    height=5
)

admin_rename_select = Select(
    Format("{item[name]}"),
    id="rename_select",
    item_id_getter=lambda g: g["id"],
    items="result",
    on_click=admin_rename_event_selected,
)

admin_rename_group = ScrollingGroup(
    admin_rename_select,
    id="admin_rename_group",
    width=1,
    height=5
)