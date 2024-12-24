from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_admin_inline_keyboard():
    inline_keyboard_builder = InlineKeyboardBuilder()

    inline_keyboard_builder.button(
        text="Добавить скамера  ➕", callback_data="add_scammer"
    )
    inline_keyboard_builder.button(
        text="Удалить скамера  ➖", callback_data="delete_scammer"
    )
    inline_keyboard_builder.button(
        text="Получить весь список скамеров (Excel-файл)  📊", callback_data="get_scammer_list"
    )
    inline_keyboard_builder.button(
       text="Узнать количество пользователей  👥", callback_data="get_count_users"
    )
    inline_keyboard_builder.button(
       text="Добавить реф. ссылку", callback_data="add_ref"
    )
    inline_keyboard_builder.button(
       text="Удалить реф. ссылку", callback_data="delete_ref"
    )

    inline_keyboard_builder.adjust(2, 1)

    return inline_keyboard_builder.as_markup()


def get_text_edit_keyboard():
    kb = ReplyKeyboardBuilder()

    kb.button(text="Продолжить без изменений")

    return kb.as_markup(
        resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Напишите отредактированный текст..."
    )



def get_apply_photos_inline_keyboard():
    inline_keyboard_builder = InlineKeyboardBuilder()

    inline_keyboard_builder.button(
        text="Далее", callback_data="apply_photos"
    )

    return inline_keyboard_builder.as_markup()


def get_back_inline_keyboard():
    inline_keyboard_builder = InlineKeyboardBuilder()

    inline_keyboard_builder.button(
        text="Назад", callback_data="admin"
    )

    return inline_keyboard_builder.as_markup()