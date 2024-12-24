import logging
from aiogram import Bot, Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.core.utils.messages import get_start_message, get_garants_message, get_tg_support_message
from src.core.keyboards.basic import get_main_menu_keyboard, get_check_keyboard, get_useful_keyboard, \
    get_go_to_menu_keyboard, get_back_keyboard
from src.core.schemas import UserScheme
from src.core.services import user_service, scammers_service, ref_service
from src.core.utils.media import create_media
from src.core.utils.scammers import create_message_about_scammer


basic_router = Router()
logger = logging.getLogger(__name__)
F: Message


@basic_router.message(Command("start"))
async def start(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()

    photo_path = r"./assets/media/systems/menu.png"
    await message.answer_photo(
        FSInputFile(photo_path),
        caption=get_start_message(message),
        reply_markup=get_main_menu_keyboard(message.from_user.id)
    )

    user = UserScheme(**message.from_user.model_dump())
    
    ref_title = command.args
    if ref_title:
        ref = await ref_service.get_ref_by_title(ref_title)
        if not ref:
            await user_service.add_user(user)
            return
        user.ref_id = ref.id

    await user_service.add_user(user)


@basic_router.message(F.text == "Проверить пользователя 🔍")
async def check(message: Message, bot: Bot, state: FSMContext):
    await state.clear()

    await message.answer(
        "Уточните, каким способом искать мошенника в базе\n\n"
        "Рекомендуем проверять пользователей через ID\n\n" 
        "Бот для проверки ID - @username_to_id_bot",
        reply_markup=get_check_keyboard(),
    )


@basic_router.message(Command("add_to_channel"))
async def start(message: Message):
    user = UserScheme(**message.from_user.model_dump())
    await user_service.add_user(user)

    photo_path = r"./assets/media/systems/admin.PNG"
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
        return await message.answer("Данный канал не был найден в базе, но будьте осторожны")

    await create_media(scammer, proof, message, bot, msg)


@basic_router.message(F.user_shared)
async def get_contact(message: Message, bot: Bot):
    scammer = await scammers_service.get_scammer(message.user_shared.user_id)

    proof = None
    msg = ""

    if scammer:
        proof, msg = await create_message_about_scammer(scammer)
    else:
        return await message.answer(f"Данный пользователь в базе не найден, но будьте осторожны! ID {message.text}")

    await create_media(scammer, proof, message, bot, msg)


class ScammerSearchState(StatesGroup):
    get_scammer_id = State()
    get_scammer_username = State()


@basic_router.message(F.text == "Проверить по ID")
async def get_text_contact(message: Message, state: FSMContext):
    await message.answer("Введите ID пользователя:", reply_markup=get_back_keyboard())
    await state.set_state(ScammerSearchState.get_scammer_id)


@basic_router.message(F.text == "Проверить по Username")
async def get_text_contact(message: Message, state: FSMContext):
    await message.answer("Введите Username пользователя:", reply_markup=get_back_keyboard())
    await state.set_state(ScammerSearchState.get_scammer_username)


@basic_router.message(ScammerSearchState.get_scammer_id)
async def get_scammer_id(message: Message, state: FSMContext, bot: Bot):
    try:
        scammer_id = int(message.text)
    except ValueError as e:
        logger.error(e)
        await message.answer("Введите корректный ID", reply_markup=get_back_keyboard())
    else:
        scammer = await scammers_service.get_scammer(scammer_id)

        if not scammer:
            await message.answer(
                f"Данный пользователь в базе не найден, но будьте осторожны! ID {message.text}",
                reply_markup=get_back_keyboard()
            )
            await state.clear()
            return

        proof, msg = await create_message_about_scammer(scammer)
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
        await message.answer(
            f"Данный пользователь в базе не найден, но будьте осторожны! Юзернейм {message.text}",
            reply_markup=get_back_keyboard()
        )
        return
    await create_media(scammer, proof, message, bot, msg)

    await state.clear()


@basic_router.message(F.text == "Полезное 💡")
async def useful(message: Message, bot: Bot, state: FSMContext):
    await state.clear()

    await message.answer(
        "Выберите интересующий раздел",
        reply_markup=get_useful_keyboard(),
    )


@basic_router.message(F.text == "Гаранты")
async def garants(message: Message, bot: Bot, state: FSMContext):
    await state.clear()

    await message.answer(
        get_garants_message(),
        reply_markup=get_go_to_menu_keyboard(),
    )


@basic_router.message(F.text == "Поддержка TG")
async def useful(message: Message, bot: Bot, state: FSMContext):
    await state.clear()

    await message.answer(
        get_tg_support_message(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=get_go_to_menu_keyboard(),
    )
