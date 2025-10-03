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