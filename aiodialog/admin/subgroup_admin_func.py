from aiogram_dialog import DialogManager

from aiodialog.StatsGroup import AdminSubSg


async def admin_sg_panel(c, w, manager: DialogManager):
    await manager.start(AdminSubSg.panel)