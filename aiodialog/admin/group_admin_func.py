from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram.types import Message
from aiodialog.StatsGroup import GroupsSg, AdminGroupSg
from db.requests import create_subgroup, del_sg, del_group, rename_group, rename_sg


async def get_group_admin_panel(c, w, manager: DialogManager):
    await manager.start(AdminGroupSg.panel)

async def start_add_subgroup(c, w, manager: DialogManager):
    await manager.start(AdminGroupSg.add_sg)

async def admin_group_getter(dialog_manager: DialogManager, **kwargs):
    state = dialog_manager.middleware_data["state"]
    data = await state.get_data()
    group_id = data.get("group_id")

    return {"group_id": group_id}

async def admin_back_button(c, w, manager: DialogManager):
    await manager.start(GroupsSg.my_subgroups)

async def create_new_subgroup(message: Message, widget: ManagedTextInput, manager: DialogManager, result: list):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    group_id = data.get("group_id")
    for subgroup in result:
        await create_subgroup(name=subgroup, group_id=group_id)
    if len(result) == 1:
        await message.answer("Подгруппа была успешно добавлена")
    else:
        await message.answer("Подгруппы были успешно добавлены")
    await manager.start(GroupsSg.my_subgroups)

async def start_del_subgroup(c, w, manager: DialogManager):
    await manager.start(AdminGroupSg.del_sg)

async def admin_subgroup_selected(c, w, manager: DialogManager, item_id):
    await del_sg(int(item_id))
    print("удалена подгруппа" + item_id)
    await manager.start(GroupsSg.my_subgroups)

async def admin_group_delete(c, w, manager: DialogManager):
    await manager.start(AdminGroupSg.del_group)

async def delete_group(c, w, manager: DialogManager):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    group_id = data.get("group_id")
    await del_group(group_id=group_id)
    await manager.start(GroupsSg.my_groups)

async def del_cancel(c, w, manager: DialogManager):
    await manager.start(AdminGroupSg.panel)

async def rename_group_button(c, w, manager: DialogManager):
    await manager.start(AdminGroupSg.rename_group)

async def rename_group_success(message: Message, widget: ManagedTextInput, manager: DialogManager, result):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    group_id = data.get("group_id")
    await rename_group(group_id=int(group_id), new_name=result)
    await manager.start(GroupsSg.my_groups)

async def rename_sg_button(c, w, manager: DialogManager):
    await manager.start(AdminGroupSg.rename_sg)

async def admin_rn_sg_selected(c, w, manager: DialogManager, item_id):
    sg_now = int(item_id)
    state = manager.middleware_data["state"]
    await state.update_data(sg_rename_now=sg_now)
    await manager.start(AdminGroupSg.finish_sg)

async def rename_subgroup(message: Message, widget: ManagedTextInput, manager: DialogManager, result):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    sg_id = data.get("sg_rename_now")
    await rename_sg(sg_id=int(sg_id), new_name=result)
    await manager.start(GroupsSg.my_subgroups)

async def admin_cancel_button(c, w, manager: DialogManager):
    await manager.start(AdminGroupSg.panel)