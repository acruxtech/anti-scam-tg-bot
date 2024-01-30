from aiogram import Bot, Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.media_group import MediaGroupBuilder

from src.messages import get_start_message
from src.keyboards.basic import get_main_menu_keyboard
from src.entities.users.schemas import UserScheme
from src.entities.users.service import user_service
from src.entities.scammers.service import scammers_service
from src.entities.scammers.models import proof_repository, scam_media_repository

basic_router = Router()

F: Message


@basic_router.message(Command("start"))
async def start(message: Message, bot: Bot):
    photo_path = r"./media/systems/menu.png"
    await message.answer_photo(
        FSInputFile(photo_path),
        caption=get_start_message(message),
        reply_markup=get_main_menu_keyboard(message.from_user.id)
    )
    user = UserScheme(**message.from_user.model_dump())
    await user_service.add_user(user)


@basic_router.message(F.user_shared)
async def get_contact(message: Message, bot: Bot):
    scammer = await scammers_service.get_scammer(message.user_shared.user_id)

    proof = None

    info_about_scammer = f"<b>Информация о пользователе:</b>\n\n" \
                         f"ID = <code>{message.user_shared.user_id}</code>"

    if scammer and scammer.is_scam:
        proof = await proof_repository.get_by_scammer_id(scammer.id)

        scammer_message = "Этот пользователь - мошенник!   ❌"
        if scammer.username:
            info_about_scammer += f"\n\nUsername = <code>{scammer.username}</code>"

        if scammer.first_name:
            info_about_scammer += f"\n\nFirst Name = <code>{scammer.first_name}</code>"
    else:
        scammer_message = "Данный пользователь не был найден в базе, но будьте осторожны"

    await message.answer(f"{scammer_message}\n\n"
                         f"{info_about_scammer}")

    if proof:
        media = await scam_media_repository.get_list(
            scam_media_repository.model.scammer_id == scammer.id
        )

        if len(media) > 0:
            album_builder = MediaGroupBuilder(
                caption=proof.text
            )

            for media_object in media:
                if media_object.type == "photo":
                    album_builder.add_photo(media=media_object.file_id)
                elif media_object.type == "video":
                    album_builder.add_video(media=media_object.file_id)

            await bot.send_media_group(message.chat.id, album_builder.build())


class ScammerSearchState(StatesGroup):
    get_scammer_id = State()
    get_scammer_username = State()


@basic_router.message(F.text == "Проверить по ID")
async def get_text_contact(message: Message, state: FSMContext):
    await message.answer("Введите ID пользователя:")
    await state.set_state(ScammerSearchState.get_scammer_id)


@basic_router.message(F.text == "Проверить по Username")
async def get_text_contact(message: Message, state: FSMContext):
    await message.answer("Введите Username пользователя:")
    await state.set_state(ScammerSearchState.get_scammer_username)


@basic_router.message(ScammerSearchState.get_scammer_id)
async def get_scammer_id(message: Message, state: FSMContext):
    try:
        scammer_id = int(message.text)
    except ValueError as e:
        print(e)
        await message.answer("Введите корректный ID")
    else:
        scammer = await scammers_service.get_scammer(scammer_id)

        info_about_scammer = f"<b>Информация о пользователе:</b>\n\n" \
                             f"ID = <code>{scammer_id}</code>"

        if scammer and scammer.is_scam:
            scammer_message = "Этот пользователь - мошенник!   ❌"
            if scammer.username:
                info_about_scammer += f"\n\nUsername = <code>{scammer.username}</code>"

            if scammer.first_name:
                info_about_scammer += f"\n\nFirst Name = <code>{scammer.first_name}</code>"
        else:
            scammer_message = "Данный пользователь не был найден в базе, но будьте осторожны"

        await message.answer(f"{scammer_message}\n\n"
                             f"{info_about_scammer}")

        await state.clear()


@basic_router.message(ScammerSearchState.get_scammer_username)
async def get_scammer_username(message: Message, state: FSMContext):
    username = message.text.strip().replace("@", "")
    scammer = await scammers_service.get_scammer_by_username(username)

    info_about_scammer = ""

    if scammer and scammer.is_scam:

        info_about_scammer = f"<b>Информация о пользователе:</b>\n\n" \
                             f"ID = <code>{scammer.id}</code>"

        scammer_message = "Этот пользователь - мошенник!   ❌"
        if scammer.username:
            info_about_scammer += f"\n\nUsername = <code>{scammer.username}</code>"

        if scammer.first_name:
            info_about_scammer += f"\n\nFirst Name = <code>{scammer.first_name}</code>"
    else:
        scammer_message = "Данный пользователь не был найден в базе, но будьте осторожны"

    await message.answer(f"{scammer_message}\n\n"
                         f"{info_about_scammer}")

    await state.clear()

