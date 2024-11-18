import json
import logging
from aiogram import Bot, Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, ChatMemberUpdated
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.messages import get_start_message
from src.keyboards.basic import get_main_menu_keyboard, get_check_keyboard, get_useful_keyboard, get_go_to_menu_keyboard
from src.entities.users.schemas import UserScheme
from src.entities.users.service import user_service
from src.entities.scammers.service import scammers_service
from src.entities.refs.service import ref_service
from src.entities.scammers.models import proof_repository
from src.utils.media import create_media
from src.utils.scammers import create_message_about_scammer

basic_router = Router()
logger = logging.getLogger(__name__)

F: Message


@basic_router.message(Command("start"))
async def start(message: Message, command: CommandObject, bot: Bot, state: FSMContext):
    await state.clear()

    photo_path = r"./media/systems/menu.png"
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
async def start(message: Message, bot: Bot):
    user = UserScheme(**message.from_user.model_dump())
    await user_service.add_user(user)

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

    await create_media(scammer, proof, message, bot, msg)


@basic_router.message(F.user_shared)
async def get_contact(message: Message, bot: Bot):
    scammer = await scammers_service.get_scammer(message.user_shared.user_id)

    proof = None
    msg = ""

    if scammer:
        proof, msg = await create_message_about_scammer(scammer)
    else:
        await message.answer(f"Данный пользователь в базе не найден, но будьте осторожны! ID {message.text}")

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
            await message.answer(f"Данный пользователь в базе не найден, но будьте осторожны! ID {message.text}")
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
        await message.answer(f"Данный пользователь в базе не найден, но будьте осторожны! Юзернейм {message.text}")
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
        "@el_capitano8\n"
        "@hooligan154\n"
        "@SEgarant\n"
        "@aizek\n"
        "@hozyaintelegi\n"
        "@Qu3rs\n",
        reply_markup=get_go_to_menu_keyboard(),
    )


@basic_router.message(F.text == "Поддержка TG")
async def useful(message: Message, bot: Bot, state: FSMContext):
    await state.clear()

    await message.answer(
        """
<b>Почта/сайты поддержки Телеграм:</b>

Официальный Телеграм FAQ — https://telegram.org/faq

Задать вопрос (волонтерам) в приложении — Меню -> настройки -> задать вопрос

Сообщить о нелегальном контенте в Телеграм —  abuse@telegram.org

Разблокировать аккаунт, канал, группу, бота — recover@telegram.org

Нарушения авторских прав (DMCA) — dmca@telegram.org

Ошибки и предложения — https://bugs.telegram.org

Проблемы со входом — sms@telegram.org

Жалоба на стикеры — sticker@telegram.org

Детское насилие — stopCA@telegram.org

Общая поддержка — support@telegram.org

Вопросы безопасности — security@telegram.org

<b>Полезные Боты:</b>

Сообщить о мошенниках — @NoToScam
Связь с пресс службой — @PressBot
Информация о блокировке — @spambot
Конфиденциальность данных — @EURegulation
Получение занятого никнейма — @username_bot
Добавить мошенника/канал в базу скамеров - @AntiSkamTG_bot

<b>Будьте внимательны:</b> у Телеграм нет других официальных учетных записей службы поддержки ни в каких 
других социальных сетях. Официальный источник: https://telegram.org/faq#telegram-support
""",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=get_go_to_menu_keyboard(),
    )
