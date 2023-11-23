from aiogram.filters.callback_data import CallbackData


class ContactMessage(CallbackData, prefix="contact"):
    id: int
