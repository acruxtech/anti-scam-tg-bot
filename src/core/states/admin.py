from aiogram.fsm.state import StatesGroup, State


class AdminForm(StatesGroup):
    get_user = State()
    get_username = State()
    get_proofs = State()
    apply_proofs = State()
    get_reason = State()
    delete_user = State()


class AddRef(StatesGroup):
    here_title = State()


class DeleteRef(StatesGroup):
    here_number = State()
