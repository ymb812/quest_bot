from aiogram.fsm.state import State, StatesGroup


class MainMenuStateGroup(StatesGroup):
    menu = State()
    start_info = State()
    help = State()
