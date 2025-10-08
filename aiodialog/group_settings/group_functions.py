from aiogram_dialog import DialogManager

from aiodialog.StatsGroup import GroupsSg
from db.requests import get_user_groups


async def groups_getter(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user.id
    groups = await get_user_groups(user)
    return {
        "result": groups,
    }

async def on_group_selected(c, w, manager: DialogManager, item_id):
    group_id = int(item_id)
    state = manager.middleware_data["state"]
    await state.update_data(group_id=group_id)
    await manager.start(state=GroupsSg.my_subgroups)
