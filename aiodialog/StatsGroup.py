from aiogram.fsm.state import State, StatesGroup

class StartSg(StatesGroup):
    start = State()
    choice = State()

class CreateSg(StatesGroup):
    name = State()
    subgroups = State()
    admins = State()

