import logging

from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, ADMINISTRATOR, IS_MEMBER
)

from src.core.services import scammers_service, chat_service, user_service
from src.core.schemas import ChatScheme


router = Router()
logger = logging.getLogger(__name__)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=ADMINISTRATOR))
async def bot_added_as_admin(event: ChatMemberUpdated, bot: Bot):
    await bot.send_message(
        event.chat.id,
        "Привет! Я бот защиты от мошенников. Моя задача - обеспечить безопасность чата. "
        "Если у вас есть подозрения или вопросы касательно какой-то личности, не стесняйтесь обращаться ко мне. "
        "Давайте работать вместе для защиты нашего чата от недобросовестных действий! 💪🛡"
    )
    await bot.send_message(
        event.from_user.id,
        f"Успешно! Вы добавили меня в <b>{event.chat.title}</b>!\n\n"
        f"Теперь мошенники не смогут вступить в ваш канал.",
    )
    chat = ChatScheme(
        id=event.chat.id,
        title=event.chat.title,
    )
    await chat_service.add_chat(chat)


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER))
async def check_new_member(event: ChatMemberUpdated, bot: Bot):
    scammer = await scammers_service.get_scammer_by_all(event.from_user.id, event.from_user.username)

    if scammer and scammer.id == event.from_user.id:
        logger.info(f"Пользователь найден! Был забанен! id = {scammer.id}, username = {scammer.username}")
        await bot.ban_chat_member(event.chat.id, event.from_user.id)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER))
async def bot_deleted(event: ChatMemberUpdated, bot: Bot):
    if event.chat.type == "private":
        if event.new_chat_member.status == 'kicked':
            await user_service.update_user_status(event.chat.id, True)
        if event.old_chat_member.status == "kicked":
            await user_service.update_user_status(event.chat.id, False)
    else:
        await bot.send_message(
            event.from_user.id,
            f"Вы удалили меня из группы <b>{event.chat.title}</b>!"
            f"Теперь ваш канал находится под угрозой!"
        )
        await chat_service.delete_chat(event.chat.id)
