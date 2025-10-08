from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput

from aiodialog.StatsGroup import AdminEventSg, GroupsSg
from db.requests import delete_event, rename_event
from aiogram.types import Message

async def admin_del_event(c, w, manager: DialogManager):
    await manager.start(AdminEventSg.del_event)

async def admin_rename_event(c, w, manager: DialogManager):
    await manager.start(AdminEventSg.rename_event)

async def admin_delete_event_selected(c, w, manager: DialogManager, item_id):
    event_now = int(item_id)
    state = manager.middleware_data["state"]
    await state.update_data(event_admin_now=event_now)
    await delete_event(event_now)
    await manager.start(GroupsSg.my_events)

async def admin_rename_event_selected(c, w, manager: DialogManager, item_id):
    event_now = int(item_id)
    state = manager.middleware_data["state"]
    await state.update_data(event_admin_now=event_now)
    await manager.start(AdminEventSg.finish_event)

async def get_event_admin_panel(c, w, manager: DialogManager):
    await manager.start(AdminEventSg.panel)

async def rename_event_success(message: Message, widget: ManagedTextInput,
                                manager: DialogManager, result: str):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    event_id = data.get("event_admin_now")
    await rename_event(event_id=event_id, new_name=result)
    print(result, event_id)
    await manager.start(GroupsSg.my_events)