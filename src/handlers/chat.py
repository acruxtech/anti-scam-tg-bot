from contextlib import suppress

from aiogram import Router, Bot, F
from aiogram.types import ChatMemberUpdated, InlineQueryResultArticle, InputTextMessageContent, InlineQuery, ChosenInlineResult
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, ADMINISTRATOR, IS_MEMBER
)

from src.entities.scammers.service import scammers_service
from src.entities.chats.schemas import ChatScheme
from src.entities.chats.service import chat_service
from src.entities.users.service import user_service


router = Router()


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
        print(f"Пользователь найден! Был забанен! id = {scammer.id}, username = {scammer.username}")
        await bot.ban_chat_member(event.chat.id, event.from_user.id)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER))
async def bot_deleted(event: ChatMemberUpdated, bot: Bot):
    await bot.send_message(
        event.from_user.id,
        f"Вы удалили меня из группы <b>{event.chat.title}</b>!"
        f"Теперь ваш канал находится под угрозой!"
    )
    await chat_service.delete_chat(event.chat.id)


@router.my_chat_member()
async def my_chat_member_handler(update: ChatMemberUpdated):
    if update.new_chat_member.status == 'kicked':
        await user_service.update_user_status(update.chat.id, True)
    if update.old_chat_member.status == "kicked":
        await user_service.update_user_status(update.chat.id, False)


@router.inline_query()
async def inline(inline_query: InlineQuery, bot: Bot):
    try:
        scammer_id = int(inline_query.query)
    except BaseException:
        return

    scammer = await scammers_service.get_scammer(scammer_id)
    if not scammer:
        return

    results = []
    results.append(
        InlineQueryResultArticle(
            id="0",
            title="Заблокировать",
            input_message_content=InputTextMessageContent(
                message_text=f"❌Пользователь ID <a href='https://t.me/{scammer.username}'>{scammer_id}</a> <b>найден в базе</b> и заблокирован во всех чатах, в которых бот состоит как админ\n\n@AntiSkamTG_bot",
                parse_mode="html",
                disable_web_page_preview=True,
            )
        )
    )
    await inline_query.answer(results, is_personal=True)


@router.chosen_inline_result()
async def inline_here_id(chosen_result: ChosenInlineResult, bot: Bot):
    scammer_id = int(chosen_result.query)

    chats = await chat_service.get_chats()
    for chat in chats:
        with suppress(BaseException):
            await bot.ban_chat_member(chat.id, scammer_id)
    
