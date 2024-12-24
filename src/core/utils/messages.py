from aiogram.types import Message


def get_start_message(message: Message) -> str:
    start_message = f"""
<b>AntiSkamTG – <i>Не дай себя обмануть.</i></b> 

<b>Добавляй</b> скам-пользователя/канал в <b>нашего бота.</b>

<b>Узнавай больше про TG:</b> <a href="https://t.me/prosto_telegram1">PROSTO TELEGRAM</a>
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


def get_garants_message() -> str:
    return (
        "@el_capitano8\n"
        "@hooligan154\n"
        "@SEgarant\n"
        "@aizek\n"
        "@hozyaintelegi\n"
        "@Qu3rs\n"
    )


def get_tg_support_message() -> str:
    return """
<b>Почта/сайты поддержки Телеграм:</b>

Официальный Телеграм FAQ — https://telegram.org/faq

Задать вопрос (волонтерам) в приложении — Меню -> настройки -> задать вопрос

Сообщить о нелегальном контенте в Телеграм —  abuse@telegram.org

Разблокировать аккаунт, канал, группу, бота — recover@telegram.org

Нарушения авторских прав (DMCA) — dmca@telegram.org

Ошибки и предложения — https://bugs.telegram.org

Проблемы со входом — sms@telegram.org

Жалоба на стикеры — sticker@telegram.org

Детское насилие — stopCA@telegram.org

Общая поддержка — support@telegram.org

Вопросы безопасности — security@telegram.org

<b>Полезные Боты:</b>

Сообщить о мошенниках — @NoToScam
Связь с пресс службой — @PressBot
Информация о блокировке — @spambot
Конфиденциальность данных — @EURegulation
Получение занятого никнейма — @username_bot
Добавить мошенника/канал в базу скамеров - @AntiSkamTG_bot

<b>Будьте внимательны:</b> у Телеграм нет других официальных учетных записей службы поддержки ни в каких 
других социальных сетях. Официальный источник: https://telegram.org/faq#telegram-support
    """