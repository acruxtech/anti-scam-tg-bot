from aiogram import Bot
from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder

from src.entities.scammers.models import scam_media_repository


async def create_media(scammer, proof, message: Message, bot: Bot):
    media = await scam_media_repository.get_last_true_proofs(scammer.id)
    media = set(tuple(item) for item in media)
    media = list(media)
    media = sorted(media, key=lambda x: x[0])

    print("-" * 50)
    print(media)
    print("-" * 50)

    if len(media) > 0:
        album_builder = MediaGroupBuilder(
            caption=f"<b>Причина:</b> {proof.text}"
        )

        for media_object in media:
            if media_object.type == "photo":
                album_builder.add_photo(media=media_object.file_id)
            elif media_object.type == "video":
                album_builder.add_video(media=media_object.file_id)

        await bot.send_media_group(message.chat.id, album_builder.build())
    else:
        await bot.send_message(message.chat.id, f"<b>Причина:</b> {proof.text}")
