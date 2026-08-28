from aiogram.fsm.state import StatesGroup, State


class AdminState(StatesGroup):
    register_admin = State()
    select_date = State()
    get_date_for_excel = State()
    get_document = State()
    generate_excel = State()

