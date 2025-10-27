from aiogram_dialog import DialogManager

from aiodialog.StatsGroup import GroupsSg
from db.requests import get_user_groups, remove_user_from_group


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

async def leave_group_button(c, w, manager: DialogManager):
    await manager.switch_to(GroupsSg.correct_leave)

async def leave_group(c, w, manager: DialogManager):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    group_id = data["group_id"]
    user_id = c.from_user.id
    await remove_user_from_group(user_id, group_id)
    await manager.switch_to(GroupsSg.my_groups)

async def leave_cancel(c, w, manager: DialogManager):
    await manager.switch_to(GroupsSg.my_subgroups)