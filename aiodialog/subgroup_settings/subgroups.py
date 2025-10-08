from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format

from aiodialog.subgroup_settings.sg_functions import on_subgroup_selected

subgroups_select = Select(
    Format("{item.name}"),
    id="subgroups_select",
    item_id_getter=lambda x: x.sg_id,
    items="result",
    on_click=on_subgroup_selected,
)

subgroups_group = ScrollingGroup(
    subgroups_select,
    id="subgroups_group",
    width=1,
    height=5
)