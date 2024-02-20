from aiogram.types import Message


def get_start_message(message: Message) -> str:
    start_message = f"""
<b>AntiSkamBot</b> – твой <b>незаменимый помощник</b> во время работы в телеграмме. 

<b>Проверяй</b> исполнителя услуг на честность <b>с помощью нашего бота.</b>

<b>Узнавай больше про ТГ:</b> @keroytg / <a href="https://t.me/+PXCfc4FyhMVjMzQ6">Rakhimov ВЕЩАЕТ</a>

<b>Агентство</b> – <a href="https://t.me/spaceagency1">Space Agency</a>

<b>Наши чаты –</b> <a href="https://t.me/+qNqoUOqi3-gzM2Yy">Админские Веселья</a> / <a href="https://t.me/zorchatik">Комитет Админов</a>
"""
    return start_message


def get_start_message_old(message: Message) -> str:
    start_message = f"""Привет, <b>{message.from_user.first_name}</b>! 👋
    
Я бот 🤖, который занимается проверкой мошенников, и могу предоставить тебе:
    
- Информацию о степени надежности и доверия к человеку, предоставляющего услуги в Telegram по ID ℹ👨‍💻️
    
- Возможность добавить скамера в базу мошенников ✍️🚫"""
    return start_message


def get_about_scammer_message(scammer) -> str:
    if scammer.username:
        about_scammer = f"Username = @{scammer.username} \n\n" \
                        f"ID = <code>{scammer.id}</code>"
    else:
        about_scammer = f"ID = <code>{scammer.id}</code>"

    return about_scammer
