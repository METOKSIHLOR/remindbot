from aiogram_dialog.widgets.kbd import ScrollingGroup
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Select

from solo_reminders.reminders_functions import del_notify_user_selected

user_reminds_select = Select(
    text=Format("{item[name]} - {item[notify_time]}"),
    id="user_delete_select",
    item_id_getter=lambda g: g["id"],
    items="result",
    on_click=del_notify_user_selected,
)

user_notify_delete_group = ScrollingGroup(
    user_reminds_select,
    id="user_notify_delete_group",
    width=1,
    height=5
)