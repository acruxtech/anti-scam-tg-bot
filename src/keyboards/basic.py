from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButtonRequestUser, KeyboardButton


def get_main_menu_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()

    request_button = KeyboardButton(
        text="Проверить профиль  🔍", request_user=KeyboardButtonRequestUser(request_id=1)
    )

    keyboard_builder.add(request_button)
    keyboard_builder.button(text="Добавить мошенника  ✍")
    keyboard_builder.button(text="Связаться с нами  📞")

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Выбери действие..."
    )


def get_send_user_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()

    request_button = KeyboardButton(
        text="Скинуть пользователя", request_user=KeyboardButtonRequestUser(request_id=2)
    )

    keyboard_builder.add(request_button)

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Скинь пользователя..."
    )
