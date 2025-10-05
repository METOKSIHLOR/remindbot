from aiogram_dialog import DialogManager

from aiodialog.StatsGroup import GroupsSg
from db.requests import get_subgroups

async def on_subgroup_selected(c, w, dialog_manager: DialogManager, item_id):
    sg_id = int(item_id)
    state = dialog_manager.middleware_data["state"]
    await state.update_data(sg_now=sg_id)
    await dialog_manager.start(GroupsSg.my_events)

async def subgroups_getter(dialog_manager: DialogManager, **kwargs):
    group_id = dialog_manager.start_data.get("group_id")
    subgroups = await get_subgroups(group_id)
    return {"subgroups": subgroups}