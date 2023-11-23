from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.utils.callbacks import ContactMessage, ReportMessage


def get_contact_answer(contact_message_id: int):
    inline_keyboard_builder = InlineKeyboardBuilder()

    inline_keyboard_builder.button(
        text="Ответить пользователю", callback_data=ContactMessage(id=contact_message_id)
    )

    inline_keyboard_builder.adjust(1)

    return inline_keyboard_builder.as_markup()


def get_report_message(reported_id: int, scammer_report_id: int):
    inline_keyboard_builder = InlineKeyboardBuilder()

    inline_keyboard_builder.button(
        text="Добавить  ✅", callback_data=ReportMessage(
            id=scammer_report_id, decision=True, reported_id=reported_id
        )
    )

    inline_keyboard_builder.button(
        text="Отклонить  ❌", callback_data=ReportMessage(
            id=scammer_report_id, decision=False, reported_id=reported_id
        )
    )

    inline_keyboard_builder.adjust(1)

    return inline_keyboard_builder.as_markup()
