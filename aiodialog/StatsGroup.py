from aiogram.fsm.state import State, StatesGroup

class StartSg(StatesGroup):
    start = State()
    main_menu = State()

class CreateSg(StatesGroup):
    name = State()
    subgroups = State()
    admins = State()

class GroupsSg(StatesGroup):
    my_groups = State()
    my_subgroups = State()
    my_events = State()
    select_event = State()

class EventsSg(StatesGroup):
    name = State()
    time = State()
    notify_time = State()
    comment = State()

class AdminGroupSg(StatesGroup):
    panel = State()
    add_sg = State()
    del_sg = State()
    del_group = State()
    rename_group = State()
    rename_sg = State()
    finish_sg = State()
    del_user = State()

class AdminEventSg(StatesGroup):
    panel = State()
    del_event = State()
    rename_event = State()
    finish_event = State()

class EditEventSg(StatesGroup):
    panel = State()
    start_time = State()
    time = State()
    notify_event = State()
    start_comment = State()
    comment = State()

class JoinSg(StatesGroup):
    id = State()
    main = State()
    choice = State()