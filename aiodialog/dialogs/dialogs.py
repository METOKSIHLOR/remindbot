from functools import partial

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Row
from aiodialog.StatsGroup import CreateSg, StartSg, GroupsSg, EventsSg, AdminGroupSg, AdminEventSg, EditEventSg, JoinSg
from aiodialog.admin.event_admin_func import get_event_admin_panel, admin_rename_event, admin_del_event, \
    rename_event_success, admin_edit_event, edit_time_success, edit_comment_success, admin_edit_comm, admin_start_time, \
    admin_join_button
from aiodialog.admin.group_admin_func import get_group_admin_panel, admin_group_getter, admin_back_button, \
    start_add_subgroup, \
    create_new_subgroup, start_del_subgroup, admin_group_delete, delete_group, del_cancel, rename_group_success, \
    rename_group_button, rename_sg_button, rename_subgroup, admin_cancel_button
from aiodialog.admin.admins import admin_sg_group, admin_rn_sg_group, admin_delete_group, admin_rename_group, \
    admin_time_group, admin_comm_group
from aiodialog.create_group.functions import name_check, correct_check, failed_check, subgroups_check, \
    finish_create, back_button, cancel_button
from aiodialog.event_settings.event_functions import start_add_event, event_name_check, event_name_success, \
    event_name_fail, event_time_check, event_time_success, event_time_fail, event_comment_success, comment_check, \
    event_comment_fail, event_getter, event_info_getter
from aiodialog.event_settings.events import events_group
from aiodialog.group_settings.group_functions import groups_getter
from aiodialog.group_settings.groups import main_menu, groups_group
from aiodialog.join_group.join_functions import join_getter, accept_join_button, reject_join_button, id_check, \
    id_check_success
from aiodialog.join_group.joins import user_joins_group
from aiodialog.start_menu.menu_functions import set_lang, groups_button, cr_button, jn_button, sl_button
from aiodialog.subgroup_settings.sg_functions import subgroups_getter
from aiodialog.subgroup_settings.subgroups import subgroups_group

start_dialog = Dialog(
    Window(
        Const("Please choose your native language."),
        Button(text=Const("Русский язык"), id="button_ru", on_click=partial(set_lang, lang="ru")),
        Button(text=Const("English"), id="button_en", on_click=partial(set_lang, lang="en")),
        Button(text=Const("Český jazyk"),id="button_cz", on_click=partial(set_lang, lang="cz")),
        state=StartSg.start),
    Window(
        Const("Выберите действие:"),
        Row(
            Button(text=Const("Мои группы"), id="my_groups", on_click=groups_button),
        ),
        Row(
            Button(text=Const("Создать группу"), id="create_button", on_click=cr_button),
            Button(text=Const("Вступить в группу"), id="join_button", on_click=jn_button),
        ),
        Button(text=Const("Одиночные напоминания"), id="solo_button", on_click=sl_button),
        state=StartSg.main_menu),
)


create_dialog = Dialog(
    Window(
        Const("Придумайте название для группы"),
        TextInput(id="Name_input", type_factory=name_check,
                  on_success=correct_check,
                  on_error=failed_check),
        Button(text=Const("Отмена"), id="cancel_button", on_click=cancel_button),
        state=CreateSg.name
    ),
    Window(Const(text="Теперь введите подгруппы в формате 'Subgroup 1, Subgroup 2, Subgroup 3'"),
           TextInput(id="Subgroups_input", type_factory=subgroups_check,
                     on_success=finish_create,
                     on_error=failed_check),
           Button(text=Const("Назад"), id="back_button", on_click=back_button),
           Button(text=Const("Отмена"), id="cancel_button", on_click=cancel_button),
           state=CreateSg.subgroups),
)

groups_dialog = Dialog(
    Window(
        Const(text="Ваши группы:"),
        groups_group,
        Button(text=Const("Главное меню"), id="main_menu", on_click=main_menu),
        state=GroupsSg.my_groups,
        getter=groups_getter,),
    Window(
        Const(text="Ваши подгруппы:"),
        subgroups_group,
        Button(text=Const("Admin panel"), id="group_admin_panel", on_click=get_group_admin_panel, when="is_admin"),
        Button(text=Const("Назад"), id="back", on_click=back_button),
        Button(text=Const("Главное меню"), id="main_menu", on_click=main_menu),
        state=GroupsSg.my_subgroups,
        getter=subgroups_getter,),
    Window(
        Const(text="События в данной подгруппе:"),
        events_group,
        Button(text=Const("Admin-panel"), id="sg_admin_panel", on_click=get_event_admin_panel, when="is_admin"),
        Button(text=Const("Назад"), id="back", on_click=back_button),
        Button(text=Const("Главное меню"), id="main_menu", on_click=main_menu),
        state=GroupsSg.my_events,
        getter=event_getter),
    Window(
        Format("Событие: {result.name}"),
        Format("Когда: {result.timestamp}"),
        Format("Комментарии: {result.comment}"),
        Button(text=Const("Назад"), id="back", on_click=back_button),
        state=GroupsSg.select_event,
        getter=event_info_getter
    )
    )

event_dialog = Dialog(
    Window(
        Const(text="Введите название события:"),
        TextInput(id="event_name_input", type_factory=event_name_check,
                  on_success=event_name_success,
                  on_error=event_name_fail),
        Button(text=Const("Отменить"), id="back", on_click=get_event_admin_panel),
        state=EventsSg.name
    ),
    Window(
        Const(text="Теперь введите время его проведения в формате пока не придумал:"),
        TextInput(id="event_time_input", type_factory=event_time_check,
                  on_success=event_time_success,
                  on_error=event_time_fail,),
        Button(text=Const("Назад"), id="back", on_click=back_button),
        Button(text=Const("Отменить"), id="back", on_click=get_event_admin_panel),
        state=EventsSg.time),
    Window(
        Const(text="Теперь введите комментарий к этому событию:"),
        TextInput(id="event_comment_input", type_factory=comment_check,
                  on_success=event_comment_success,
                  on_error=event_comment_fail,),
        Button(text=Const("Назад"), id="back", on_click=back_button),
        Button(text=Const("Отменить"), id="back", on_click=get_event_admin_panel),
        state=EventsSg.comment
    )
)

group_admin_dialog = Dialog(
    Window(
        Format(text="Айди группы: {group_id}"),
        Row(
            Button(text=Const("Добавить подгруппу"), id="add_sg", on_click=start_add_subgroup),
            Button(text=Const("Удалить подгруппу"), id="del_sg", on_click=start_del_subgroup),
        ),
        Row(
            Button(text=Const("Переименовать группу"), id="rename_group", on_click=rename_group_button),
            Button(text=Const("Переименовать подгруппу"), id="rename_subgroup", on_click=rename_sg_button),
        ),
        Button(text=Const("Запросы на вступление"), id="join_admin", on_click=admin_join_button),
        Button(text=Const("Удалить группу"), id="del_group", on_click=admin_group_delete),
        Button(text=Const("Назад"), id="admin_back_button", on_click=admin_back_button),
        state=AdminGroupSg.panel,
        getter=admin_group_getter
    ),
    Window(
        Const(text="Теперь введите подгруппы в формате 'Subgroup 1, Subgroup 2, Subgroup 3'"),
        TextInput(id="Subgroups_input", type_factory=subgroups_check,
                  on_success=create_new_subgroup,
                  on_error=failed_check),
        Button(text=Const("Отменить"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.add_sg
    ),
    Window(
        Const(text="Теперь выберите какую подгруппу вы хотите удалить."),
        admin_sg_group,
        Button(text=Const("Отменить"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.del_sg,
        getter=subgroups_getter,
    ),
    Window(
        Const(text="Вы уверены?"),
        Row(
            Button(text=Const("Да"), id="yes_del", on_click=delete_group),
            Button(text=Const("Нет"), id="no_del", on_click=del_cancel)
        ),
        state=AdminGroupSg.del_group
    ),
    Window(
        Const(text="Введите новое название группы"),
        TextInput(
            id="rename_group_input",
            type_factory=name_check,
            on_success=rename_group_success,
            on_error=failed_check,
        ),
        Button(text=Const("Отменить"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.rename_group,
    ),
    Window(
        Const(text="Выберите подгруппу"),
        admin_rn_sg_group,
        Button(text=Const("Отменить"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.rename_sg,
        getter=subgroups_getter,
    ),
    Window(
        Const(text="Введите новое название подгруппы"),
        TextInput(
            id="rename_subgroup_input",
            type_factory=name_check,
            on_success=rename_subgroup,
            on_error=failed_check,
        ),
        Button(text=Const("Отменить"), id="admin_cancel", on_click=admin_cancel_button),
        state=AdminGroupSg.finish_sg,
    )
)

subgroups_admin_dialog = Dialog(
    Window(
        Const(text="Админ-панель"),
        Row(Button(text=Const("Удалить событие"), id="event_delete", on_click=admin_del_event),
            Button(text=Const("Добавить событие"), id="add_event", on_click=start_add_event),),
        Button(text=Const("Редактировать событие"), id="event_edit", on_click=admin_edit_event),
        Button(text=Const("Отменить"), id="back", on_click=get_event_admin_panel),
        state=AdminEventSg.panel,
    ),
    Window(Const(text="Выберите событие:"),
           admin_delete_group,
           Button(text=Const("Отменить"), id="back", on_click=admin_cancel_button),
           state=AdminEventSg.del_event,
           getter=event_getter,),
    Window(Const(text="Выберите событие:"),
           admin_rename_group,
           Button(text=Const("Отменить"), id="back", on_click=get_event_admin_panel),
           state=AdminEventSg.rename_event,
           getter=event_getter,),
    Window(Const(text="Введите новое название события:"),
           TextInput(id="rename_subgroup_input", type_factory=name_check,
                     on_success=rename_event_success,
                     on_error=failed_check,),
           Button(text=Const("Назад"), id="back", on_click=back_button),
           Button(text=Const("Отменить"), id="back", on_click=get_event_admin_panel),
           state=AdminEventSg.finish_event,
           )
)

edit_event_dialog = Dialog(
    Window(
        Const(text="Админ-панель"),
        Row(
            Button(text=Const("Изменить комментарий"), id="comm_edit", on_click=admin_edit_comm),
            Button(text=Const("Изменить время"), id="event_time_edit", on_click=admin_start_time),),
        Button(text=Const("Переименовать событие"), id="event_rename", on_click=admin_rename_event),
        Button(text=Const("Назад"), id="back", on_click=get_event_admin_panel),
        state=EditEventSg.panel,
    ),
    Window(
      Const(text="Выберите событие:"),
        admin_time_group,
        Button(text=Const("Отменить"), id="back", on_click=get_event_admin_panel),
        state=EditEventSg.start_time,
        getter=event_getter,
    ),
    Window(Const(text="Введите новое время:"),
           TextInput(id="event_time_edit", type_factory=event_time_check,
                     on_success=edit_time_success,
                     on_error=event_time_fail, ),
           Button(text=Const("Назад"), id="back", on_click=back_button),
           Button(text=Const("Отменить"), id="back", on_click=get_event_admin_panel),
           state=EditEventSg.time,
           ),
    Window(Const(text="Выберите событие:"),
           admin_comm_group,
           state=EditEventSg.start_comment,
           getter=event_getter,),
    Window(Const(text="Введите новый комментарий:"),
           TextInput(id="rename_comment_input",
                     type_factory=comment_check,
                     on_success=edit_comment_success,
                     on_error=failed_check),
           state=EditEventSg.comment,)
)

join_dialog = Dialog(
    Window(
        Const(text="Введите айди группы. Его можно узнать у владельца:"),
        TextInput(id="join_group_input", type_factory=id_check,
                  on_success=id_check_success,
                  on_error=failed_check),
        state=JoinSg.id
    ),
    Window(
        Const(text="Пользователи, желающие вступить в данную группу:"),
        user_joins_group,
        state=JoinSg.main,
        getter=join_getter
    ),
    Window(
        Const(text="Принять пользователя в группу?"),
        Row(
            Button(text=Const("Принять"), id="accept_join", on_click=accept_join_button),
            Button(text=Const("Отклонить"), id="reject_join", on_click=reject_join_button),
        ),
        state=JoinSg.choice,
    )
)