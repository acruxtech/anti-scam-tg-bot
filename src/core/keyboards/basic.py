from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButtonRequestUser, KeyboardButton, KeyboardButtonRequestChat
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

from src.config import OWNER_IDS

from src.core.utils.callbacks import AddScamer


def get_main_menu_keyboard(user_id: int):
    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text="Проверить пользователя 🔍")

    request_button = KeyboardButton(
        text="Проверить канал  📢", request_chat=KeyboardButtonRequestChat(request_id=6, chat_is_channel=True)
    )

    keyboard_builder.add(request_button)
    keyboard_builder.button(text="Добавить мошенника ✍️")
    keyboard_builder.button(text="Связаться с нами  📞")
    keyboard_builder.button(text="Полезное 💡")

    if user_id in OWNER_IDS:
        keyboard_builder.button(text="Зайти в админку  📊")
        keyboard_builder.adjust(1, 1, 2, 1, 1)
    else:
        keyboard_builder.adjust(1, 1, 2, 1)

    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=False, input_field_placeholder="Выбери действие..."
    )


def get_check_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()

    request_button = KeyboardButton(
        text="Отправить профиль 🔍", request_user=KeyboardButtonRequestUser(request_id=1)
    )

    keyboard_builder.add(request_button)
    keyboard_builder.button(text="Проверить по ID")
    keyboard_builder.button(text="Проверить по Username")
    keyboard_builder.adjust(1, 2)

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
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(text="Отправить репорт 🚩", callback_data=AddScamer(action="send_report").pack())
    keyboard_builder.button(text="Сбросить фото 📸", callback_data=AddScamer(action="reset").pack())
    keyboard_builder.button(text="Назад", callback_data=AddScamer(action="menu").pack())

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()


def get_apply_send_keyboard(scammer_id: int):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Разослать", callback_data=f"apply_send_{scammer_id}")
    return keyboard_builder.as_markup()


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


def get_back_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text="Назад")
    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=True,
    )


def get_username_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text="Продолжить без username")
    keyboard_builder.button(text="Назад")
    keyboard_builder.adjust(1, 1)
    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Скиньте username?"
    )


def get_useful_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text="Гаранты")
    keyboard_builder.button(text="Поддержка TG")
    keyboard_builder.button(text="Назад")
    keyboard_builder.adjust(2, 1)
    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=True,
    )


def get_go_to_menu_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text="Назад")
    return keyboard_builder.as_markup(
        resize_keyboard=True, one_time_keyboard=True,
    )
