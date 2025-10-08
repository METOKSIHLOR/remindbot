from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format

from aiodialog.event_settings.event_functions import on_event_selected
from aiodialog.subgroup_settings.sg_functions import on_subgroup_selected

events_select = Select(
    Format("{item[name]}"),
    id="events_select",
    item_id_getter=lambda x: x["id"],
    items="result",
    on_click=on_event_selected,
)

events_group = ScrollingGroup(
    events_select,
    id="events_group",
    width=1,
    height=5
)