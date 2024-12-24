from aiogram.filters.callback_data import CallbackData


class ContactMessage(CallbackData, prefix="contact"):
    id: int


class ProofMessage(CallbackData, prefix="proof"):
    id: int
    user_id: int
    decision: bool
    scammer_id: int


class AddScamer(CallbackData, prefix="add_scamer"):
    action: str
