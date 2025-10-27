from aiogram import Bot
from aiogram_dialog import DialogManager

from aiodialog.StatsGroup import AdminGroupSg, GroupsSg, StartSg, JoinSg
from db.requests import get_joins, get_one_join, add_user_group, delete_join, get_group, exist_join, \
    create_join_request, user_in_group


async def on_join_selected(c, w, manager: DialogManager, item_id):
    state = manager.middleware_data["state"]
    await state.update_data(join_item_id=item_id)
    await manager.switch_to(JoinSg.choice)

async def join_getter(dialog_manager: DialogManager, **kwargs):
    state = dialog_manager.middleware_data["state"]
    data = await state.get_data()
    group_id = data["group_id"]
    joins = await get_joins(group_id)

    result = []
    for join in joins:
        result.append({
            "id": join.id,
            "user_id": join.user.telegram_id,
            "name": join.user.first_name,
        })

    return {"result": result}

async def accept_join_button(c, w, manager: DialogManager):
    state = manager.middleware_data["state"]
    bot: Bot = manager.middleware_data["bot"]
    data = await state.get_data()
    group_id = data["group_id"]
    join_id = data["join_item_id"]
    join = await get_one_join(id=int(join_id))
    await add_user_group(group_id=group_id, user_id=join.user.telegram_id)
    await bot.send_message(
        chat_id=join.user.telegram_id,
        text=f"Vaše žádost o připojení ke skupině {group_id} byla schválena!")
    await delete_join(id=int(join_id))
    await c.answer("✅ Žádost byla zpracována")
    await manager.start(AdminGroupSg.panel)

async def reject_join_button(c, w, manager: DialogManager):
    state = manager.middleware_data["state"]
    bot: Bot = manager.middleware_data["bot"]
    data = await state.get_data()
    group_id = data["group_id"]
    join_id = int(data["join_item_id"])
    join = await get_one_join(id=join_id)
    await bot.send_message(
        chat_id=join.user.telegram_id,
        text=f"Vaše žádost o připojení ke skupině {group_id} byla zamítnuta!")
    await delete_join(id=join_id)
    await c.answer("✅ Žádost byla zpracována")
    await manager.start(AdminGroupSg.panel)

def id_check(text: str):
    if not text.isdigit() or len(text) > 10:
        raise ValueError("Zdá se, že jste zadali něco jiného než ID")
    return text

async def id_check_success(c, w, manager: DialogManager, result: str):
    user_id = c.from_user.id
    group_id = int(result)
    group = await get_group(group_id)
    if not group:
        await c.answer("Zdá se, že taková skupina neexistuje")
        await manager.reset_stack()
        await manager.start(StartSg.main_menu)
    if await user_in_group(user_id=user_id, group_id=group_id):
        await c.answer(text="Již jste členem této skupiny")
        await manager.reset_stack()
        await manager.start(StartSg.main_menu)
        return
    if await exist_join(user_id, group_id):
        await c.answer(text="Již jste podali žádost o připojení do této skupiny.\nProsím, počkejte na rozhodnutí vlastníka")
        await manager.reset_stack()
        await manager.start(StartSg.main_menu)
        return
    await create_join_request(user_id, group_id)
    await c.answer("Žádost byla úspěšně odeslána ke schválení")
    await manager.reset_stack()
    await manager.start(StartSg.main_menu)
