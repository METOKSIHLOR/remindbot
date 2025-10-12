from aiogram_dialog.widgets.kbd import Button, Select, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from aiodialog.join_group.join_functions import on_join_selected

user_joins_select = Select(
    Format("{item[user_id]} - {item[name]}"),
    id="join_select",
    item_id_getter=lambda g: g["id"],
    items="result",
    on_click=on_join_selected,
)

user_joins_group = ScrollingGroup(
    user_joins_select,
    id="joins_select_group",
    width=1,
    height=5
)