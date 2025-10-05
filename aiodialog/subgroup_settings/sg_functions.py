from aiogram_dialog import DialogManager

from db.requests import get_subgroups


async def subgroups_getter(dialog_manager: DialogManager, **kwargs):
    group_id = dialog_manager.start_data.get("group_id")
    subgroups = await get_subgroups(group_id)
    return {"subgroups": subgroups}