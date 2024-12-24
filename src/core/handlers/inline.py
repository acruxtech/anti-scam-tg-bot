import logging
import time

import pyrogram

from aiogram import Bot, Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, ChosenInlineResult
from aiogram.fsm.state import State, StatesGroup
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import UsernameNotOccupied

from src.config import API_ID, API_HASH, USER_INFO_CHANNEL_ID
from src.core.keyboards.basic import get_inline_keyboard
from src.core.services import scammers_service, chat_service, user_info_service
from src.core.schemas import UserInfoScheme

last_request_time = {}


class InlineState(StatesGroup):
    get_user_info = State()


router = Router()
logger = logging.getLogger(__name__)


F: InlineQuery


async def send_post_to_channel(username: str, channel_id: int) -> tuple[int, str, str] | None:
    async with Client(
            "session",
            api_id=API_ID,
            api_hash=API_HASH,
    ) as client:
        user = await client.get_users(username)
        mention = pyrogram.types.MessageEntity(
            client=client,
            type=pyrogram.enums.MessageEntityType.TEXT_MENTION,
            offset=len(f"@{user.username}\nID: {user.id}\n"),
            length=len(str(user.id)),
            user=user
        )
        entities = [mention]
        sent_message = await client.send_message(
            chat_id=int(channel_id),
            text="\n".join((
                f"@{user.username}",
                f"<b>ID: </b><code>{user.id}</code>",
                "📎Вечная ссылка"
            )),
            parse_mode=ParseMode.HTML,
            entities=entities
        )
        return user.id, user.username, sent_message.link


@router.inline_query()
async def inline(inline_query: InlineQuery):
    user_id = None
    if inline_query.query.isdigit():
        user_id = int(inline_query.query)

    results = []

    if user_id:
        scammer = await scammers_service.get_scammer(user_id)
        if scammer:
            results.append(
                InlineQueryResultArticle(
                    id="block",
                    title="Заблокировать",
                    input_message_content=InputTextMessageContent(
                        message_text=f"❌Пользователь ID <a href='https://t.me/{scammer.username}'>{user_id}</a> "
                                     f"<b>найден в базе</b> и заблокирован во всех чатах, в которых бот состоит "
                                     f"как админ\n\n@AntiSkamTG_bot",
                        parse_mode="html",
                        disable_web_page_preview=True,
                    )
                )
            )
    results.append(
        InlineQueryResultArticle(
            id="user_info",
            title="Получить вечную ссылку",
            input_message_content=InputTextMessageContent(
                message_text=f"<i>Выполняется поиск... Ожидайте⏳</i>",

            ),
            reply_markup=get_inline_keyboard(),
        )
    )
    if not results:
        results.append(
            InlineQueryResultArticle(
                id="no_scammer",
                title="Пользователя нет в базе!",
                input_message_content=InputTextMessageContent(
                    message_text=f"❌Пользователя с ID {user_id} <b>нет в базе</b>. Блокировка невозможна",
                    parse_mode="html",
                    disable_web_page_preview=True,
                )
            )
        )

    await inline_query.answer(
        results,
        is_personal=True,
        cache_time=60*60*24*365,
    )


@router.chosen_inline_result()
async def inline_here_id(chosen_result: ChosenInlineResult, bot: Bot):
    if chosen_result.result_id == "no_scammer":
        return

    elif chosen_result.result_id == "block":
        user_id = int(chosen_result.query)
        chats = await chat_service.get_chats()
        for chat in chats:
            try:
                await bot.ban_chat_member(chat.id, user_id)
            except BaseException as e:
                logger.error(e)

    elif chosen_result.result_id == "user_info":
        user_id = chosen_result.from_user.id
        current_time = time.time()
        if user_id in last_request_time and current_time - last_request_time[user_id] < 60:
            await bot.edit_message_text(
                inline_message_id=chosen_result.inline_message_id,
                text="<i>Можно сделать максимум <b>один</b> запрос в минуту! Ожидайте, пожалуйста</i>",
                parse_mode="html",
            )
            return
        last_request_time[user_id] = current_time

        user_id, username = None, None
        if chosen_result.query.isdigit():
            user_info = await user_info_service.get_user_info_by_id(int(chosen_result.query))
            if user_info:
                link = user_info.link
            else:
                link = None
        else:
            user_info = await user_info_service.get_user_info_by_username(chosen_result.query.lstrip("@"))
            if user_info:
                user_id = user_info.id
                username = user_info.username
                link = user_info.link
            else:
                try:
                    user_id, username, link = await send_post_to_channel(chosen_result.query, USER_INFO_CHANNEL_ID)
                except UsernameNotOccupied:
                    await bot.edit_message_text(
                        inline_message_id=chosen_result.inline_message_id,
                        text=f"<i>Пользователя с таким юзернеймом не существует</i>",
                        parse_mode="html",
                    )
                    return
                await user_info_service.add_user_info(
                    UserInfoScheme(
                        id=user_id,
                        username=username.lstrip("@"),
                        link=link,
                    )
                )
        if link:
            await bot.edit_message_text(
                inline_message_id=chosen_result.inline_message_id,
                text=f"{username}\n"
                     f"<i>ID:</i> {user_id}\n"
                     f"<i>Вечная ссылка:</i> {link}\n",
                parse_mode="html",
            )
        else:
            await bot.edit_message_text(
                inline_message_id=chosen_result.inline_message_id,
                text=f"<i>Пользователь не найден в базе данных. Возвращайтесь позже или "
                     f"попробуйте получить вечную ссылку по юзернейму</i>",
                parse_mode="html",
            )
