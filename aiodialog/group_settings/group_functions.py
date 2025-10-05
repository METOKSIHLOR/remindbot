from aiogram_dialog import DialogManager

from aiodialog.StatsGroup import GroupsSg
from db.requests import get_user_groups


async def groups_getter(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user.id
    page = dialog_manager.dialog_data.get("page", 0)

    groups = await get_user_groups(user)
    total = len(groups)

    start = page * 8
    end = start + 8
    page_groups = groups[start:end]

    return {
        "groups": page_groups,
        "page": page,
        "total": total,
    }

async def on_group_selected(c, w, manager: DialogManager, item_id):
    group_id = int(item_id)
    await manager.start(state=GroupsSg.my_subgroups, data={"group_id": group_id})

async def on_subgroup_selected(c, w, manager: DialogManager, item_id):
    print(f"Выбрана подгруппа {item_id}")

async def change_page(c, w, manager: DialogManager, delta: int):
    page = manager.dialog_data.get("page", 0)
    new_page = max(0, page + delta)
    manager.dialog_data["page"] = new_page
    await manager.show()