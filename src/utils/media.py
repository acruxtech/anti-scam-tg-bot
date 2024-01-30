from aiogram import Bot
from aiogram.types import Message

from src.entities.scammers.models import scam_media_repository


async def create_media(scammer_id: int, message: Message, bot: Bot):
    media = await scam_media_repository.get_list(
        scam_media_repository.model.scammer_id == scammer_id
    )

    if len(media) > 0:
        scam_rep = await scammers_reports_service.get_scammer_report(scammers_reports_id)
        scammer = await scammers_service.get_scammer(scam_rep.scammer_id)

        album_builder = MediaGroupBuilder(
            caption=scam_rep.text
        )

        for media_object in media:
            if media_object.type == "photo":
                album_builder.add_photo(media=media_object.file_id)
            elif media_object.type == "video":
                album_builder.add_video(media=media_object.file_id)


    messages = await bot.send_media_group(MODERATOR_ID, album_builder.build())