from aiogram import Bot, Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.messages import get_start_message
from src.keyboards.basic import get_main_menu_keyboard
from src.entities.users.schemas import UserScheme
from src.entities.users.service import user_service
from src.entities.scammers.service import scammers_service
from src.entities.scammers.models import proof_repository
from src.utils.media import create_media
from src.utils.scammers import create_message_about_scammer

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


@basic_router.message(Command("add_to_channel"))
async def start(message: Message, bot: Bot):
    photo_path = r"./media/systems/admin.PNG"
    await message.answer_photo(
        FSInputFile(photo_path),
        caption="Чтобы я мог следить за мошенниками в вашем канале, сделайте следующее:\n\n"
                "<b>1.</b> Добавить меня в ваш канал\n"
                "<b>2.</b> Сделать меня администратором и выдать права, как на картинке\n\n"
                "После этих действий я отпишу вам, что всё прошло успешно."
    )


@basic_router.message(F.chat_shared)
async def get_chat(message: Message, bot: Bot):
    scammer = await scammers_service.get_scammer(message.chat_shared.chat_id)

    proof = None
    msg = ""

    if scammer:
        proof, msg = await create_message_about_scammer(scammer)
    else:
        await message.answer("Данный канал не был найден в базе, но будьте осторожны")

    if proof:
        await create_media(scammer, proof, message, bot, msg)


@basic_router.message(F.user_shared)
async def get_contact(message: Message, bot: Bot):
    scammer = await scammers_service.get_scammer(message.user_shared.user_id)

    proof = None
    msg = ""

    if scammer:
        proof, msg = await create_message_about_scammer(scammer)
    else:
        await message.answer("Данный пользователь не был найден в базе, но будьте осторожны")

    if proof:
        await create_media(scammer, proof, message, bot, msg)


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
async def get_scammer_id(message: Message, state: FSMContext, bot: Bot):
    try:
        scammer_id = int(message.text)
    except ValueError as e:
        print(e)
        await message.answer("Введите корректный ID")
    else:
        scammer = await scammers_service.get_scammer(scammer_id)

        if not scammer:
            await message.answer("Пользователь не был найден в базе")
            await state.clear()
            return

        proof, msg = None, ""

        if scammer:
            proof, msg = await create_message_about_scammer(scammer)

        if proof:
            await create_media(scammer, proof, message, bot, msg)

        await state.clear()


@basic_router.message(ScammerSearchState.get_scammer_username)
async def get_scammer_username(message: Message, state: FSMContext, bot: Bot):
    username = message.text.strip().replace("@", "").replace("https://t.me/", "")

    scammer = await scammers_service.get_scammer_by_username(username)

    proof, msg = None, ""

    if scammer:
        proof, msg = await create_message_about_scammer(scammer)
    else:
        await message.answer("Пользователь не был найден в базе")

    if proof:
        await create_media(scammer, proof, message, bot, msg)

    await state.clear()
