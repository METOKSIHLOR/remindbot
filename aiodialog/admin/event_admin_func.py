from datetime import timezone, timedelta, datetime
from zoneinfo import ZoneInfo

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput

from aiodialog.StatsGroup import AdminEventSg, GroupsSg, EditEventSg, JoinSg
from db.requests import delete_event, rename_event, edit_time_event, edit_comment_event
from aiogram.types import Message

async def admin_del_event(c, w, manager: DialogManager):
    await manager.start(AdminEventSg.del_event)

async def admin_rename_event(c, w, manager: DialogManager):
    await manager.start(AdminEventSg.rename_event)

async def admin_event_cancel_button(c, w, manager: DialogManager):
    await manager.start(GroupsSg.my_events)

async def edit_event_cancel(c, w, manager: DialogManager):
    await manager.reset_stack()
    await manager.start(EditEventSg.panel)

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


async def select_time_success(c, w, manager: DialogManager, result: datetime):
    state = manager.middleware_data["state"]
    await state.update_data(event_time=result.isoformat())
    await manager.next()

async def edit_time_success(c, w, manager: DialogManager, result: int):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    event_id = data.get("admin_edit")

    event_time = datetime.fromisoformat(data.get("event_time"))
    prague_tz = ZoneInfo("Europe/Prague")
    event_time = event_time.replace(tzinfo=prague_tz)

    now_prag = datetime.now(prague_tz)
    event_time_prag = event_time.astimezone(prague_tz)
    notify_time_prag = event_time_prag - timedelta(hours=result)

    if notify_time_prag <= now_prag:
        await c.answer(
            f"❌ Připomenutí nelze nastavit do minulosti.\n"
            f"Zadejte menší počet hodin.")
    else:
        await edit_time_event(event_id=event_id, new_time=event_time, notify=result)
        await c.answer("✅ Čas a připomenutí byly úspěšně aktualizovány!")
        await manager.reset_stack()
        await manager.start(GroupsSg.my_events)

async def admin_edit_comm(c, w, manager: DialogManager):
    await manager.start(EditEventSg.start_comment)

async def edit_comment_success(c, w, manager: DialogManager, result: str):
    state = manager.middleware_data["state"]
    data = await state.get_data()
    event_id = data.get("admin_edit")
    await edit_comment_event(event_id=event_id, new_comment=result)
    await c.answer("✅ Komentář byl úspěšně změněn")
    await manager.start(GroupsSg.my_events)