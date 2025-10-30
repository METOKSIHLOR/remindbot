from datetime import datetime, timezone
from functools import partial

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Row
from sqlalchemy.sql.functions import current_time

from aiodialog.StatsGroup import CreateSg, StartSg, GroupsSg, EventsSg, AdminGroupSg, AdminEventSg, EditEventSg, JoinSg, \
    SoloSg
from aiodialog.admin.event_admin_func import get_event_admin_panel, admin_rename_event, admin_del_event, \
    rename_event_success, admin_edit_event, edit_time_success, edit_comment_success, admin_edit_comm, admin_start_time, \
    admin_join_button, admin_event_cancel_button, edit_event_cancel, select_time_success
from aiodialog.admin.group_admin_func import get_group_admin_panel, admin_group_getter, admin_back_button, \
    start_add_subgroup, \
    create_new_subgroup, start_del_subgroup, admin_group_delete, delete_group, del_cancel, rename_group_success, \
    rename_group_button, rename_sg_button, rename_subgroup, admin_cancel_button, g_admin_back_button, \
    admin_users_getter, admin_del_user
from aiodialog.admin.admins import admin_sg_group, admin_rn_sg_group, admin_delete_group, admin_rename_group, \
    admin_time_group, admin_comm_group, user_delete_group
from aiodialog.create_group.functions import name_check, correct_check, failed_check, subgroups_check, \
    finish_create, back_button, cancel_button, time_getter
from aiodialog.event_settings.event_functions import start_add_event, event_name_check, event_name_success, \
    event_name_fail, event_time_success, event_comment_success, comment_check, \
    event_comment_fail, event_getter, event_info_getter, time_type_factory, notify_check, notify_success
from aiodialog.event_settings.events import events_group
from aiodialog.group_settings.group_functions import groups_getter, leave_group_button, leave_group, leave_cancel
from aiodialog.group_settings.groups import main_menu, groups_group
from aiodialog.join_group.join_functions import join_getter, accept_join_button, reject_join_button, id_check, \
    id_check_success
from aiodialog.join_group.joins import user_joins_group
from aiodialog.start_menu.menu_functions import groups_button, cr_button, jn_button, sl_button
from aiodialog.subgroup_settings.sg_functions import subgroups_getter
from aiodialog.subgroup_settings.subgroups import subgroups_group
from solo_reminders.reminders import user_reminds_select, user_notify_delete_group
from solo_reminders.reminders_functions import add_notify_button, solo_name_success, create_solo_notify, notify_getter, del_solo_button

start_dialog = Dialog(
    Window(
        Const("ℹ️ Menu"),
        Row(
            Button(text=Const("👥 Skupiny"), id="my_groups", on_click=groups_button),
        ),
        Row(
            Button(text=Const("➕ Vytvořit skupinu"), id="create_button", on_click=cr_button),
            Button(text=Const("👨‍👩‍👦 Připojit se ke skupině"), id="join_button", on_click=jn_button),
        ),
        Button(text=Const("🔔 Osobní připomenutí"), id="solo_button", on_click=sl_button),
        state=StartSg.main_menu),
)


create_dialog = Dialog(
    Window(
        Const("Vymyslete název pro skupinu"),
        TextInput(id="Name_input", type_factory=name_check,
                  on_success=correct_check,
                  on_error=failed_check),
        Button(text=Const("❌ Zrušit"), id="cancel_button", on_click=cancel_button),
        state=CreateSg.name
    ),
    Window(Const(text="Nyní zadejte podskupiny ve formátu 'Podskupina1, Podskupina2, Podskupina3'"),
           TextInput(id="Subgroups_input", type_factory=subgroups_check,
                     on_success=finish_create,
                     on_error=failed_check),
           Button(text=Const("↩️ Zpět"), id="back_button", on_click=back_button),
           Button(text=Const("❌ Zrušit"), id="cancel_button", on_click=cancel_button),
           state=CreateSg.subgroups),
)

groups_dialog = Dialog(
    Window(
        Const(text="👥 Vaše skupiny:"),
        groups_group,
        Button(text=Const("ℹ️ Hlavní menu"), id="main_menu", on_click=main_menu),
        state=GroupsSg.my_groups,
        getter=groups_getter,),
    Window(
        Const(text="👥 Podskupiny:"),
        subgroups_group,
        Button(text=Const("🚪 Opustit skupinu"), id="leave_group", on_click=leave_group_button, when="not_admin"),
        Button(text=Const("⚙️ Nastavení"), id="group_admin_panel", on_click=get_group_admin_panel, when="is_admin"),
        Button(text=Const("↩️ Zpět"), id="back", on_click=back_button),
        Button(text=Const("ℹ️ Hlavní menu"), id="main_menu", on_click=main_menu),
        state=GroupsSg.my_subgroups,
        getter=subgroups_getter,),
    Window(
        Const(text="Události v této podskupině:"),
        events_group,
        Button(text=Const("⚙️ Nastavení"), id="sg_admin_panel", on_click=get_event_admin_panel, when="is_admin"),
        Button(text=Const("↩️ Zpět"), id="back", on_click=back_button),
        Button(text=Const("ℹ️ Hlavní menu"), id="main_menu", on_click=main_menu),
        state=GroupsSg.my_events,
        getter=event_getter),
    Window(
        Format("Událost: {result.name}"),
        Format("\nKdy: {result.timestamp}"),
        Format("\nKomentář: {result.comment}"),
        Button(text=Const("↩️ Zpět"), id="back", on_click=back_button),
        state=GroupsSg.select_event,
        getter=event_info_getter
    ),
    Window(
        Const(text="Jste si jisti?"),
        Row(
            Button(text=Const("✅ Ano"), id="yes_leave", on_click=leave_group),
            Button(text=Const("❌ Ne"), id="no_leave", on_click=leave_cancel)
        ),
        state=GroupsSg.correct_leave,
    ),
    )

event_dialog = Dialog(
    Window(
        Const(text="Zadejte název události:"),
        TextInput(id="event_name_input", type_factory=event_name_check,
                  on_success=event_name_success,
                  on_error=event_name_fail),
        Button(text=Const("❌ Zrušit"), id="back", on_click=get_event_admin_panel),
        state=EventsSg.name
    ),
    Window(
        Format(text="Nyní zadejte čas konání ve formátu 'HH:MM DD.MM.RRRR' ({current_time}):"),
        TextInput(id="event_time_input", type_factory=time_type_factory,
                  on_success=event_time_success,
                  on_error=failed_check,),
        Button(text=Const("↩️ Zpět"), id="back", on_click=back_button),
        Button(text=Const("❌ Zrušit"), id="cancel_button", on_click=get_event_admin_panel),
        state=EventsSg.time,
        getter=time_getter),
    Window(
        Const(text="Zadejte, kolik hodin před událostí chcete připomenutí:"),
        TextInput(id="event_notify_input", type_factory=notify_check, on_success=notify_success, on_error=failed_check),
        Button(text=Const("↩️ Zpět"), id="back", on_click=back_button),
        Button(text=Const("❌ Zrušit"), id="cancel_button", on_click=get_event_admin_panel),
        state=EventsSg.notify_time,
    ),
    Window(
        Const(text="Zadejte komentář k této události:"),
        TextInput(id="event_comment_input", type_factory=comment_check,
                  on_success=event_comment_success,
                  on_error=event_comment_fail,),
        Button(text=Const("↩️ Zpět"), id="back", on_click=back_button),
        Button(text=Const("❌ Zrušit"), id="back", on_click=get_event_admin_panel),
        state=EventsSg.comment
    )
)

group_admin_dialog = Dialog(
    Window(
        Format(text="ID skupiny: {group_id}"),
        Row(
            Button(text=Const("➕ Přidat podskupinu"), id="add_sg", on_click=start_add_subgroup),
            Button(text=Const("➖ Odstranit podskupinu"), id="del_sg", on_click=start_del_subgroup),
        ),
        Row(
            Button(text=Const("🖊 Přejmenovat skupinu"), id="rename_group", on_click=rename_group_button),
            Button(text=Const("🖊 Přejmenovat podskupinu"), id="rename_subgroup", on_click=rename_sg_button),
        ),
        Row(
            Button(text=Const("📋 Žádosti o připojení"), id="join_admin", on_click=admin_join_button),
            Button(text=Const("⛔️ Odstranit uživatele"), id="del_user", on_click=admin_del_user)),
        Button(text=Const("⚠️ Odstranit skupinu"), id="del_group", on_click=admin_group_delete),
        Button(text=Const("↩️ Zpět"), id="admin_back_button", on_click=admin_back_button),
        state=AdminGroupSg.panel,
        getter=admin_group_getter
    ),
    Window(Const(text="Vyberte uživatele:"),
        user_delete_group,
        Button(text=Const("❌ Zrušit"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.del_user,
        getter=admin_users_getter,
    ),
    Window(
        Const(text="Zadejte podskupiny ve formátu 'Podskupina1, Podskupina2, Podskupina3'"),
        TextInput(id="Subgroups_input", type_factory=subgroups_check,
                  on_success=create_new_subgroup,
                  on_error=failed_check),
        Button(text=Const("❌ Zrušit"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.add_sg
    ),
    Window(
        Const(text="Vyberte, kterou podskupinu chcete odstranit."),
        admin_sg_group,
        Button(text=Const("❌ Zrušit"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.del_sg,
        getter=subgroups_getter,
    ),
    Window(
        Const(text="Jste si jisti?"),
        Row(
            Button(text=Const("✅ Ano"), id="yes_del", on_click=delete_group),
            Button(text=Const("❌ Ne"), id="no_del", on_click=del_cancel)
        ),
        state=AdminGroupSg.del_group
    ),
    Window(
        Const(text="Zadejte nový název skupiny:"),
        TextInput(
            id="rename_group_input",
            type_factory=name_check,
            on_success=rename_group_success,
            on_error=failed_check,
        ),
        Button(text=Const("❌ Zrušit"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.rename_group,
    ),
    Window(
        Const(text="Vyberte podskupinu:"),
        admin_rn_sg_group,
        Button(text=Const("❌ Zrušit"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.rename_sg,
        getter=subgroups_getter,
    ),
    Window(
        Const(text="Zadejte nový název podskupiny:"),
        TextInput(
            id="rename_subgroup_input",
            type_factory=name_check,
            on_success=rename_subgroup,
            on_error=failed_check,
        ),
        Button(text=Const("↩️ Zpět"), id="g_admin_back_button", on_click=g_admin_back_button),
        Button(text=Const("❌ Zrušit"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.finish_sg,
    )
)

subgroups_admin_dialog = Dialog(
    Window(
        Const(text="Nastavení"),
        Row(Button(text=Const("➕ Přidat událost"), id="add_event", on_click=start_add_event),
            Button(text=Const("➖ Odstranit událost"), id="event_delete", on_click=admin_del_event),),
        Button(text=Const("🖊 Upravit událost"), id="event_edit", on_click=admin_edit_event),
        Button(text=Const("↩️ Zpět"), id="back", on_click=admin_event_cancel_button),
        state=AdminEventSg.panel,
    ),
    Window(Const(text="Vyberte událost:"),
           admin_delete_group,
           Button(text=Const("❌ Zrušit"), id="back", on_click=get_event_admin_panel),
           state=AdminEventSg.del_event,
           getter=event_getter,),
    Window(Const(text="Vyberte událost:"),
           admin_rename_group,
           Button(text=Const("❌ Zrušit"), id="back", on_click=get_event_admin_panel),
           state=AdminEventSg.rename_event,
           getter=event_getter,),
    Window(Const(text="Zadejte nový název události:"),
           TextInput(id="rename_subgroup_input", type_factory=name_check,
                     on_success=rename_event_success,
                     on_error=failed_check,),
           Button(text=Const("↩️ Zpět"), id="back", on_click=back_button),
           Button(text=Const("❌ Zrušit"), id="back", on_click=get_event_admin_panel),
           state=AdminEventSg.finish_event,
           )
)

edit_event_dialog = Dialog(
    Window(
        Const(text="Nastavení"),
        Row(
            Button(text=Const("✉️ Upravit komentář"), id="comm_edit", on_click=admin_edit_comm),
            Button(text=Const("⏱️ Upravit čas"), id="event_time_edit", on_click=admin_start_time),),
        Button(text=Const("📅 Přejmenovat událost"), id="event_rename", on_click=admin_rename_event),
        Button(text=Const("↩️ Zpět"), id="back", on_click=get_event_admin_panel),
        state=EditEventSg.panel,
    ),
    Window(
      Const(text="Vyberte událost:"),
        admin_time_group,
        Button(text=Const("❌ Zrušit"), id="back", on_click=edit_event_cancel),
        state=EditEventSg.start_time,
        getter=event_getter,
    ),
    Window(Format(text="Nyní zadejte čas konání ve formátu 'HH:MM DD.MM.RRRR' ({current_time}):"),
        TextInput(id="event_time_input", type_factory=time_type_factory,
                  on_success=select_time_success,
                  on_error=failed_check,),
           Button(text=Const("↩️ Zpět"), id="back", on_click=back_button),
           Button(text=Const("❌ Zrušit"), id="back", on_click=edit_event_cancel),
           state=EditEventSg.time,
           getter=time_getter,
           ),
    Window(
        Const(text="Zadejte, kolik hodin před událostí chcete připomenutí:"),
        TextInput(id="event_notify_input", type_factory=notify_check,
                  on_success=edit_time_success,
                  on_error=failed_check),
        Button(text=Const("↩️ Zpět"), id="back", on_click=back_button),
        Button(text=Const("❌ Zrušit"), id="back", on_click=edit_event_cancel),
        state=EditEventSg.notify_event,),
    Window(Const(text="Vyberte událost:"),
           admin_comm_group,
           Button(text=Const("❌ Zrušit"), id="back", on_click=edit_event_cancel),
           state=EditEventSg.start_comment,
           getter=event_getter,),
    Window(Const(text="Zadejte nový komentář:"),
           TextInput(id="rename_comment_input",
                     type_factory=comment_check,
                     on_success=edit_comment_success,
                     on_error=failed_check),
           Button(text=Const("↩️ Zpět"), id="back", on_click=get_event_admin_panel),
           Button(text=Const("❌ Zrušit"), id="back", on_click=edit_event_cancel),
           state=EditEventSg.comment,)
)

join_dialog = Dialog(
    Window(
        Const(text="Zadejte ID skupiny.\nZískáte ho od vlastníka:"),
        TextInput(id="join_group_input", type_factory=id_check,
                  on_success=id_check_success,
                  on_error=failed_check),
        Button(text=Const("❌ Zrušit"), id="cancel_button", on_click=cancel_button),
        state=JoinSg.id
    ),
    Window(
        Const(text="Uživatelé, kteří se chtějí připojit ke skupině:"),
        user_joins_group,
        Button(text=Const("❌ Zrušit"), id="admin_cancel", on_click=admin_cancel_button),
        state=JoinSg.main,
        getter=join_getter
    ),
    Window(
        Const(text="Přijmout uživatele do skupiny?"),
        Row(
            Button(text=Const("✅ Schválit"), id="accept_join", on_click=accept_join_button),
            Button(text=Const("❌ Odmítnout"), id="reject_join", on_click=reject_join_button),
        ),
        Button(text=Const("↩️ Zpět"), id="g_admin_back_button", on_click=g_admin_back_button),
        Button(text=Const("❌ Zrušit"), id="admin_cancel", on_click=admin_cancel_button),
        state=JoinSg.choice,
    )
)

solo_dialog = Dialog(
    Window(
        Const(text="Osobní připomenutí"),
        Row(
            Button(text=Const("✅ Přidat"), id="add_notify", on_click=add_notify_button),
            Button(text=Const("❌ Odstranit"), id="del_notify", on_click=del_solo_button),
        ),
        Button(text=Const("ℹ️ Hlavní menu"), id="cancel_button", on_click=main_menu),
        state=SoloSg.main,
    ),
    Window(
        Const(text="Zadejte název události:"),
        TextInput(type_factory=name_check, id="solo_name_input", on_success=solo_name_success, on_error=failed_check),
        Button(text=Const("❌ Zrušit"), id="cancel_button", on_click=main_menu),
        state=SoloSg.add_name,
    ),
    Window(Format(text="Zadejte čas konání ve formátu 'HH:MM DD.MM.RRRR' ({current_time}):"),
           TextInput(id="solo_time_input", type_factory=time_type_factory,
                  on_success=create_solo_notify,
                  on_error=failed_check,),
           Button(text=Const("↩️ Zpět"), id="back", on_click=back_button),
           Button(text=Const("❌ Zrušit"), id="cancel_button", on_click=main_menu),
           state=SoloSg.add_time,
           getter=time_getter,
    ),
    Window(Const(text="Vaše aktuální události:"),
        user_notify_delete_group,
        Button(text=Const("❌ Zrušit"), id="cancel_button", on_click=main_menu),
        state=SoloSg.del_notify,
        getter=notify_getter
    ),
)