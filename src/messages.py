from aiogram.types import Message


def get_start_message(message: Message) -> str:
    start_message = f"""
<b>AntiSkamTG – <i>Не дай себя обмануть.</i></b> 

<b>Проверяй</b> пользователя/канал на честность <b>с помощью нашего бота.</b>

<b>Узнавай больше про ТГ:</b> <a href="https://t.me/+qyKIFJSJ0DwzZmUy">Жилка Предпринимателя</a> / <a href="https://t.me/+PXCfc4FyhMVjMzQ6">Rakhimov ВЕЩАЕТ</a>

<b>Агентство</b> – <a href="https://t.me/spaceagency1">Space Agency</a>

<b>Наш чат</b> – <a href="https://t.me/+Ech10tlczSs1ZmFi">Комитет Админов</a>

<b>Партнёр</b> - <a href="https://t.me/adm_blackhole">BLACK HOLE</a>
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
