from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButtonRequestUser, KeyboardButton, KeyboardButtonRequestChat
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

from src.config import OWNER_IDS


def get_main_menu_keyboard(user_id: int):
    keyboard_builder = ReplyKeyboardBuilder()

    request_button = KeyboardButton(
        text="Проверить профиль  🔍", request_user=KeyboardButtonRequestUser(request_id=1)
    )

    keyboard_builder.add(request_button)
    keyboard_builder.button(text="Проверить по ID")
    keyboard_builder.button(text="Проверить по Username")

    request_button = KeyboardButton(
        text="Проверить канал  📢", request_chat=KeyboardButtonRequestChat(request_id=6, chat_is_channel=True)
    )

    keyboard_builder.add(request_button)
    keyboard_builder.button(text="Кинуть репорт  ✍")
    keyboard_builder.button(text="Связаться с нами  📞")

    if user_id in OWNER_IDS:
        keyboard_builder.button(text="Зайти в админку  📊")
        keyboard_builder.adjust(1, 2, 1, 2)
    else:
        keyboard_builder.adjust(1, 2, 1, 2)

    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Выбери действие..."
    )


def get_report_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text="На пользователя  👤")
    keyboard_builder.button(text="На канал  📢")
    keyboard_builder.button(text="Назад")

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="На кого кидаете репорт?"
    )


def get_send_channel_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()

    request_button = KeyboardButton(
        text="Скинуть канал", request_chat=KeyboardButtonRequestChat(request_id=3, chat_is_channel=True)
    )

    keyboard_builder.add(request_button)

    keyboard_builder.button(text="Назад")

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Скинь канал..."
    )


def get_send_user_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()

    request_button = KeyboardButton(
        text="Скинуть пользователя", request_user=KeyboardButtonRequestUser(request_id=2)
    )

    keyboard_builder.add(request_button)

    keyboard_builder.button(text="Назад")

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Скиньте пользователя..."
    )


def get_send_media_scammer_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text="Отправить репорт 🚩")
    keyboard_builder.button(text="Сбросить фото 📸")
    keyboard_builder.button(text="Назад")

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Что делаем с репортом?"
    )


def get_contact_cancel_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text="Назад")

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Что произошло?"
    )


def get_empty_keyboard():
    # keyboard_builder = ReplyKeyboardBuilder()
    # keyboard_builder.adjust(1)
    # return keyboard_builder.as_markup()
    return ReplyKeyboardRemove(remove_keyboard=True)


def get_username_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text="Продолжить без username")
    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Скиньте username?"
    )
