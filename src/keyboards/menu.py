from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.utils.callbacks import ContactMessage


def get_contact_answer(contact_message_id: int):
    inline_keyboard_builder = InlineKeyboardBuilder()

    inline_keyboard_builder.button(
        text="Ответить пользователю", callback_data=ContactMessage(id=contact_message_id)
    )

    inline_keyboard_builder.adjust(1)

    return inline_keyboard_builder.as_markup()
