from aiogram import Bot
from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder

from src.db.models import ScammerMedia
from src.core.services import scammers_service


DEFAULT_TEXT_SUFFIX_PROOF = "\n\nРекомендую проверять пользователей/каналы через @AntiSkamTG_bot"


async def create_media(scammer, proof, message: Message, bot: Bot, msg: str,
                       chat_id: int = None, with_suffix: bool = True):
    media = await scammers_service.get_last_true_proofs(scammer.id)
    media = set(tuple(item) for item in media)
    media = list(media)
    media = sorted(media, key=lambda x: x[0])

    media = [ScammerMedia(
        id=item[0],
        type=item[1],
        file_id=item[2],
        proof_id=item[3],
        scammer_id=item[4]
    ) for item in media]

    if proof:
        text = proof.text.replace(DEFAULT_TEXT_SUFFIX_PROOF, "")
    else:
        text = ""
    if with_suffix:
        text += DEFAULT_TEXT_SUFFIX_PROOF
    
    if not chat_id:
        chat_id = message.chat.id

    if len(media) > 0:
        album_builder = MediaGroupBuilder(
            caption=f"{msg}\n\n<b>Причина:</b> {text}"
        )

        for media_object in media:
            if media_object.type == "photo":
                album_builder.add_photo(media=media_object.file_id)
            elif media_object.type == "video":
                album_builder.add_video(media=media_object.file_id)

        await bot.send_media_group(chat_id, album_builder.build())
    else:
        await bot.send_message(chat_id, f"{msg}\n\n<b>Причина:</b> {text}")
