from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

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

admin_event_select = Select(
    Format("{item.name}"),
    id="event_select",
    item_id_getter=lambda g: g.sg_id,
    items="result",
    on_click=admin_subgroup_selected,
)

admin_event_group = ScrollingGroup(
    admin_sg_select,
    id="admin_sg_group",
    width=1,
    height=5
)