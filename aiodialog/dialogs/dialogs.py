from functools import partial

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Button, Row
from aiodialog.StatsGroup import CreateSg, StartSg, GroupsSg, EventsSg
from aiodialog.create_group.functions import name_check, correct_check, failed_check, subgroups_check, \
    finish_create, back_button
from aiodialog.event_settings.event_functions import start_add_event, event_name_check, event_name_success, \
    event_name_fail, event_time_check, event_time_success, event_time_fail, event_comment_success, comment_check, \
    event_comment_fail, event_getter
from aiodialog.event_settings.events import events_group
from aiodialog.group_settings.group_functions import groups_getter
from aiodialog.group_settings.groups import groups_select, next_button, prev_button, main_menu
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
        state=CreateSg.name
    ),
    Window(Const(text="Теперь введите подгруппы в формате 'Subgroup 1, Subgroup 2, Subgroup 3'"),
           TextInput(id="Subgroups_input", type_factory=subgroups_check,
                     on_success=finish_create,
                     on_error=failed_check),
           Button(text=Const("Назад"), id="back_button", on_click=back_button),
           state=CreateSg.subgroups),
)

groups_dialog = Dialog(
    Window(
        Const(text="Ваши группы:"),
        groups_select,
        Row(prev_button, next_button),
        Button(text=Const("Главное меню"), id="main_menu", on_click=main_menu),
        state=GroupsSg.my_groups,
        getter=groups_getter,),
    Window(
        Const(text="Ваши подгруппы:"),
        subgroups_group,
        Button(text=Const("Группы"), id="back", on_click=back_button),
        Button(text=Const("Главное меню"), id="main_menu", on_click=main_menu),
        state=GroupsSg.my_subgroups,
        getter=subgroups_getter,),
    Window(
        Const(text="События в данной подгруппе:"),
        events_group,
        Button(text=Const("Добавить"), id="add_event", on_click=start_add_event),
        state=GroupsSg.my_events,
        getter=event_getter),
    )

event_dialog = Dialog(
    Window(
        Const(text="Введите название события:"),
        TextInput(id="event_name_input", type_factory=event_name_check,
                  on_success=event_name_success,
                  on_error=event_name_fail),
        state=EventsSg.name
    ),
    Window(
        Const(text="Теперь введите время его проведения в формате пока не придумал:"),
        TextInput(id="event_time_input", type_factory=event_time_check,
                  on_success=event_time_success,
                  on_error=event_time_fail,),
        state=EventsSg.time),
    Window(
        Const(text="Теперь введите комментарий к этому событию:"),
        TextInput(id="event_comment_input", type_factory=comment_check,
                  on_success=event_comment_success,
                  on_error=event_comment_fail,),
        state=EventsSg.comment
    )
)