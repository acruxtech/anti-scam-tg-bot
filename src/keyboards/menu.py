from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.utils.callbacks import ContactMessage, ProofMessage


def get_contact_answer(contact_message_id: int):
    inline_keyboard_builder = InlineKeyboardBuilder()

    inline_keyboard_builder.button(
        text="Ответить пользователю", callback_data=ContactMessage(id=contact_message_id)
    )

    inline_keyboard_builder.adjust(1)

    return inline_keyboard_builder.as_markup()


def get_report_message(reported_id: int, proof_id: int, scammer_id: int):
    inline_keyboard_builder = InlineKeyboardBuilder()

    inline_keyboard_builder.button(
        text="Добавить  ✅", callback_data=ProofMessage(
            id=proof_id, decision=True, user_id=reported_id, scammer_id=scammer_id
        )
    )

    inline_keyboard_builder.button(
        text="Отклонить  ❌", callback_data=ProofMessage(
            id=proof_id, decision=False, user_id=reported_id, scammer_id=scammer_id
        )
    )

    inline_keyboard_builder.adjust(1)

    return inline_keyboard_builder.as_markup()
