from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_inline_keyboard():
    inline_keyboard_builder = InlineKeyboardBuilder()

    inline_keyboard_builder.button(
        text="Добавить скамера  ➕", callback_data="add_scamer"
    )
    inline_keyboard_builder.button(
        text="Удалить скамера  ➖", callback_data="delete_scammer"
    )
    inline_keyboard_builder.button(
        text="Получить весь список скамеров (Excel-файл)  📊", callback_data="get_scammer_list"
    )

    inline_keyboard_builder.adjust(2, 1)

    return inline_keyboard_builder.as_markup()
