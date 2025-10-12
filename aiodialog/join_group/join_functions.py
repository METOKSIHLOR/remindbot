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
        text=f"Ваша заявка на вступление в группу {group_id} была одобрена!")
    await delete_join(id=int(join_id))
    await c.answer("✅ Заявка обработана")
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
        text=f"Ваша заявка на вступление в группу {group_id} была отклонена!")
    await delete_join(id=join_id)
    await c.answer("✅ Заявка обработана")
    await manager.start(AdminGroupSg.panel)

def id_check(text: str):
    group = get_group(int(text))
    if not text.isdigit() or len(text) > 10:
        raise ValueError("Кажется, вы ввели что-то кроме айди")
    if not group:
        raise ValueError("Кажется, такая группа не существует")
    return text

async def id_check_success(c, w, manager: DialogManager, result: str):
    user_id = c.from_user.id
    group = int(result)
    """if user_in_group(user_id=user_id, group_id=group):
        await c.answer(text="Вы уже состоите в данной группе")
        await manager.reset_stack()
        await manager.start(StartSg.main_menu)
        return"""
    if await exist_join(user_id, group):
        await c.answer(text="Вы уже подавали заявку на вступление в эту группу. \nПожалуйста, дождитесь решения владельца")
        await manager.reset_stack()
        await manager.start(StartSg.main_menu)
        return
    await create_join_request(user_id, group)
    await c.answer("Заявка успешно отправлена на рассмотрение")
    await manager.reset_stack()
    await manager.start(StartSg.main_menu)

