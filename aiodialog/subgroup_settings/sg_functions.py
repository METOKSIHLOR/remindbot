from aiogram_dialog import DialogManager

from aiodialog.StatsGroup import GroupsSg
from db.requests import get_subgroups, get_group


async def on_subgroup_selected(c, w, dialog_manager: DialogManager, item_id):
    sg_id = int(item_id)
    state = dialog_manager.middleware_data["state"]
    await state.update_data(sg_now=sg_id)
    await dialog_manager.start(GroupsSg.my_events)

async def subgroups_getter(dialog_manager: DialogManager, **kwargs):
    state = dialog_manager.middleware_data["state"]
    data = await state.get_data()
    group_id = data.get("group_id")
    subgroups = await get_subgroups(group_id)
    user = dialog_manager.event.from_user.id
    group = await get_group(group_id)
    is_admin = group.owned_by == user
    await state.update_data(is_admin=is_admin)
    return {"result": subgroups, "is_admin": is_admin}
