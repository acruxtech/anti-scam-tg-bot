import logging
import pyrogram

from aiogram import Bot, Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, ChosenInlineResult
from aiogram.fsm.state import State, StatesGroup
from pyrogram import Client

from src.config import API_ID, API_HASH, USER_INFO_CHANNEL_ID
from src.core.services import scammers_service, chat_service


class InlineState(StatesGroup):
    get_user_info = State()


router = Router()
logger = logging.getLogger(__name__)


F: InlineQuery


class UserNotFoundError(Exception):
    def __init__(self, message="Пользователь не найден"):
        self.message = message
        super().__init__(self.message)


async def send_post_to_channel(username: str, channel_id: int) -> pyrogram.types.Message | None:
    # try:
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
        return await client.send_message(
            chat_id=channel_id,
            text="\n".join((
                f"@{user.username}",
                f"<b>ID: </b><code>{user.id}</code>",
                "📎Вечная ссылка"
            )),
            entities=entities
        )
    # except errors.UserNotFound:
    #     raise UserNotFoundError()
    # except Exception as e:
    #     raise Exception(f"Ошибка отправки поста: {e}")


@router.inline_query()
async def inline(inline_query: InlineQuery):
    try:
        user_id = int(inline_query.query)
    except BaseException as e:
        logger.error(e)
        return

    scammer = await scammers_service.get_scammer(user_id)
    user_sent = await send_post_to_channel(user_id, USER_INFO_CHANNEL_ID)

    results = []

    if user_sent:
        results.append(
            InlineQueryResultArticle(
                id="user_info",
                title="Получить вечную ссылку",
                input_message_content=InputTextMessageContent(
                    message_text=f"ID пользователя: {user_id}\n"
                                 f"Вечная ссылка: {user_sent.link}",
                )
            )
        )

    if scammer:
        results.append(
            InlineQueryResultArticle(
                id="block",
                title="Заблокировать",
                input_message_content=InputTextMessageContent(
                    message_text=f"❌Пользователь ID <a href='https://t.me/{scammer.username}'>{user_id}</a> <b>найден в базе</b> и заблокирован во всех чатах, в которых бот состоит как админ\n\n@AntiSkamTG_bot",
                    parse_mode="html",
                    disable_web_page_preview=True,
                )
            )
        )
    else:
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

    user_id = int(chosen_result.query)

    if chosen_result.result_id == "block":
        chats = await chat_service.get_chats()
        for chat in chats:
            try:
                await bot.ban_chat_member(chat.id, user_id)
            except BaseException as e:
                logger.error(e)
