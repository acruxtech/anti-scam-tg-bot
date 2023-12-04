from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from src.config import MODERATOR_ID

from src.keyboards.basic import (
    get_send_user_keyboard,
    get_main_menu_keyboard,
    get_send_media_scammer_keyboard,
    get_contact_cancel_keyboard,
    get_empty_keyboard
)
from src.keyboards.menu import get_report_message

from src.entities.scammers.schemas import ScammerReportSchemeCreate, ScammerAnsweredScheme
from src.entities.scammers.service import scammers_service, scammers_reports_service
from src.entities.scammers.models import scam_media_repository

from src.utils.callbacks import ReportMessage
from src.utils.scammers import get_scammer_data_from_message


scammer_router = Router()


F: Message


class AddScammerForm(StatesGroup):
    get_profile = State()
    add_profile = State()
    detect_hide_profile = State()
    get_proofs = State()
    get_media = State()
    add_scam_to_database = State()
    get_explanation = State()


@scammer_router.message(F.text == "Кинуть репорт  ✍")
async def send_scam_user(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
        f"Перешли сообщение мошенника или отправь мне его контакт", reply_markup=get_send_user_keyboard()
    )
    await state.set_state(AddScammerForm.get_profile)


@scammer_router.message(F.text == "Назад")
async def back(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Возвращаю в главное меню...", reply_markup=get_main_menu_keyboard(message.from_user.id))
    await state.clear()


@scammer_router.message(AddScammerForm.get_profile)
async def get_scam(message: Message, bot: Bot, state: FSMContext):
    if message.user_shared or message.forward_from:
        await message.answer("Мы получили профиль пользователя ✅", reply_markup=get_contact_cancel_keyboard())
        scammer = get_scammer_data_from_message(message)
        scammer_from_db = await scammers_service.add_scammer(scammer)
        await state.update_data(scammer_id=scammer_from_db.id)
        await message.answer("Распиши ситуацию, которая произошла у тебя со скаммером:")
        await state.set_state(AddScammerForm.get_proofs)
    else:
        await message.answer(
            "Пользователь либо скрыл данные о себе, либо вы отправили что-то не то \n\n"
            "Отправьте его контакт с помощью кнопки ниже 👇👇👇",
            reply_markup=get_send_user_keyboard()
        )


@scammer_router.message(F.text == "Отправить репорт 🚩")
async def send_report(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await send_post_to_moderator(message, bot, state, data["scammers_reports_id"])


async def send_post_to_moderator(message: Message, bot: Bot, state: FSMContext, scammers_reports_id: int):
    media = await scam_media_repository.get_list(
        scam_media_repository.model.scammers_reports_id == scammers_reports_id
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

        if scammer.username:
            about_scammer = f"Username = @{scammer.username} \n\n" \
                            f"ID = <code>{scammer.id}</code>"
        else:
            about_scammer = f"ID = <code>{scammer.id}</code>"

        await bot.send_message(
            MODERATOR_ID,
            f"Репорт от <b>@{message.from_user.username}</b> \n\n"
            f"На пользователя: \n\n"
            f"{about_scammer}  🛑"
        )
        messages = await bot.send_media_group(MODERATOR_ID, album_builder.build())
        message_ = messages[0]
        print("id сообщения =", message_.message_id)
        await bot.send_message(
            MODERATOR_ID, "Выберите действие:",
            reply_markup=get_report_message(message.from_user.id, scammers_reports_id)
        )
        await state.clear()
        await message.answer(
            "Ваш репорт отправился на рассмотрение...  🕒\n\n"
            "Мы сообщим наше решение по делу после рассмотрения модератором  👨‍⚖",
            reply_markup=get_main_menu_keyboard(message.from_user.id)
        )
    else:
        await message.answer("Загрузи хотя бы 1 фотографию или видео")


@scammer_router.message(AddScammerForm.get_media, F.video)
async def get_video(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    scam_report_id = data["scammers_reports_id"]
    video_id = message.video.file_id
    await scam_media_repository.create(
        {
            "file_id": video_id,
            "type": "video",
            "scammers_reports_id": scam_report_id
        }
    )


@scammer_router.message(AddScammerForm.get_media, F.photo)
async def get_photo(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    scam_report_id = data["scammers_reports_id"]
    photo_id = message.photo[0].file_id
    await scam_media_repository.create(
        {
            "file_id": photo_id,
            "type": "photo",
            "scammers_reports_id": scam_report_id
        }
    )


@scammer_router.message(AddScammerForm.get_proofs, F.text)
async def ask_proofs(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    scammer_report = ScammerReportSchemeCreate(
        text=message.text, reported_id=message.from_user.id, scammer_id=data["scammer_id"]
    )
    scammers_reports = await scammers_reports_service.create_scammer_report(scammer_report)
    await message.answer(
        "Отправь фото/видео для доказательства скама 🖼 🎥 \n\n"
        "После отправки нажмите на кнопку ниже 👇👇👇",
        reply_markup=get_send_media_scammer_keyboard()
    )
    await state.update_data(scammers_reports_id=scammers_reports.id)
    await state.set_state(AddScammerForm.get_media)


@scammer_router.callback_query(ReportMessage.filter())
async def qwe(call: CallbackQuery, bot: Bot, callback_data: ReportMessage, state: FSMContext):
    await state.update_data(scammer_report_id=callback_data.id)
    await scammers_reports_service.update_scammer_report(callback_data.id, call.message.message_id)
    if callback_data.decision:
        await bot.send_message(
            callback_data.reported_id, "Мы рассмотрели ваш репорт на пользователя и занесли его в базу! 👮‍♂\n\n"
                                       "Благодарим за помощь в борьбе с мошениками!  🤝"
        )
        await bot.edit_message_text(
            "Вы добавили мошенника в базу  ✅", call.message.chat.id, call.message.message_id
        )
        try:
            scammer_report_answered = ScammerAnsweredScheme(
                is_reviewed=True,
                reviewer_id=call.message.from_user.id,
                decision=True
            )
            scammer_report = await scammers_reports_service.answer_to_scammer_report(
                callback_data.id, scammer_report_answered
            )
            await scammers_service.confirm(scammer_report.scammer_id)
            await bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=None
            )
        except TelegramBadRequest:
            pass
    else:
        await call.message.answer("Напишите пользователю, почему вы отказали: ", reply_markup=None)
        await state.update_data(reported_id=callback_data.reported_id)
        await bot.edit_message_text(
            "Вы отклонили данный репорт  ❌", call.message.chat.id, call.message.message_id
        )
        try:
            await bot.edit_message_reply_markup(
                call.message.chat.id, call.message.message_id, reply_markup=None
            )
        except TelegramBadRequest:
            pass
        await state.set_state(AddScammerForm.get_explanation)
    await call.answer()


@scammer_router.message(AddScammerForm.get_explanation)
async def refuse_report(message: Message, bot: Bot, state: FSMContext):
    if len(message.text) > 0:
        data = await state.get_data()
        scammer_report_id = data["scammer_report_id"]
        scammer_report_answered = ScammerAnsweredScheme(
            is_reviewed=True,
            reviewer_id=message.from_user.id,
            decision=False,
            explanation=message.text
        )
        updated_scammer_report = await scammers_reports_service.answer_to_scammer_report(
            scammer_report_id, scammer_report_answered
        )
        await message.answer(
            "Причина отказа была отправлена пользователю  ✅",
            reply_markup=get_main_menu_keyboard(message.from_user.id)
        )
        await bot.send_message(
            data["reported_id"],
            f"Мы отклонили ваш репорт на пользователя c ID = <code>{updated_scammer_report.scammer_id}</code>! \n\n"
            f"Причина отказа: <b>{message.text}</b>\n\n"
            f"Попробуй подать новый репорт или написать в тех поддержку!"
        )
        await state.clear()
    else:
        await message.answer("Напишите текст")
