from aiogram.filters.callback_data import CallbackData


class ContactMessage(CallbackData, prefix="contact"):
    id: int


class ReportMessage(CallbackData, prefix="report"):
    id: int
    reported_id: int
    decision: bool
