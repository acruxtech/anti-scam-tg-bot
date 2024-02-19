from aiogram import Router, Bot, F
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, ADMINISTRATOR, IS_MEMBER
)

from src.entities.scammers.service import scammers_service


router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=ADMINISTRATOR))
async def bot_added_as_admin(event: ChatMemberUpdated, bot: Bot):
    await bot.send_message(
        event.chat.id,
        "Привет! Я бот защиты от мошенников. Моя задача - обеспечить безопасность чата."
        "Если у вас есть подозрения или вопросы касательно какой-то личности, не стесняйтесь обращаться ко мне."
        "Давайте работать вместе для защиты нашего чата от недобросовестных действий! 💪🛡"
    )
    await bot.send_message(
        event.from_user.id,
        f"Успешно! Вы добавили меня в <b>{event.chat.title}</b>!\n\n"
        f"Теперь мошенники не смогут вступить в ваш канал.",
    )


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def check_new_member(event: ChatMemberUpdated, bot: Bot):
    scammer = await scammers_service.get_scammer_by_all(event.from_user.id, event.from_user.username)

    if scammer and scammer.id == event.from_user.id:
        print(f"Пользователь найден! Был забанен! id = {scammer.id}, username = {scammer.username}")
        await bot.ban_chat_member(event.chat.id, event.from_user.id)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER))
async def bot_deleted(event: ChatMemberUpdated, bot: Bot):
    await bot.send_message(
        event.from_user.id,
        f"Вы удалили меня из группы <b>{event.chat.title}</b>!"
        f"Теперь ваш канал находится по угрозой!"
    )
