from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput

from aiodialog.StatsGroup import AdminEventSg, GroupsSg, EditEventSg, JoinSg
from db.requests import delete_event, rename_event, edit_time_event, edit_comment_event
from aiogram.types import Message

async def admin_del_event(c, w, manager: DialogManager):
    await manager.start(AdminEventSg.del_event)

async def admin_rename_event(c, w, manager: DialogManager):
    await manager.start(AdminEventSg.rename_event)

async def admin_cancel_button(c, w, manager: DialogManager):
    await manager.start(GroupsSg.my_events)

async def admin_join_button(c, w, manager: DialogManager):
    await manager.start(JoinSg.main)

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

async def admin_edit_event(c, w, manager: DialogManager):
    await manager.start(EditEventSg.panel)

async def admin_start_time(c, w, manager: DialogManager):
    await manager.start(EditEventSg.start_time)

async def admin_edit_selected(c, w, manager: DialogManager, item_id):
    state = manager.middleware_data["state"]
    await state.update_data(admin_edit=item_id)
    await manager.next()


async def edit_time_success(c, w, manager: DialogManager, result: str):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    event_id = data.get("admin_edit")
    await edit_time_event(event_id=event_id, new_time=result)
    await c.answer("Время было успешно изменено")
    await manager.start(GroupsSg.my_events)


async def admin_edit_comm(c, w, manager: DialogManager):
    await manager.start(EditEventSg.start_comment)

async def edit_comment_success(c, w, manager: DialogManager, result: str):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    event_id = data.get("admin_edit")
    await edit_comment_event(event_id=event_id, new_comment=result)
    await c.answer("Комментарий успешно изменен")
    await manager.start(GroupsSg.my_events)