from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from src.repository import IntegrityException
from src.keyboards.basic import get_send_user_keyboard, get_main_menu_keyboard
from src.entities.scammers.schemas import ScammerScheme
from src.entities.scammers.models import scammers_repository
from src.entities.scammers.service import scammers_service

scammer_router = Router()


class AddScammerForm(StatesGroup):
    get_profile = State()
    add_profile = State()
    detect_hide_profile = State()
    add_scam_to_database = State()


@scammer_router.message(F.text == "Кинуть репорт  ✍")
async def send_scam_user(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
        f"Перешли сообщение мошенника или отправь мне его контакт", reply_markup=get_send_user_keyboard()
    )
    await state.set_state(AddScammerForm.get_profile)


@scammer_router.message(AddScammerForm.get_profile, F.text == "Назад")
async def back(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Возвращаю в главное меню...", reply_markup=get_main_menu_keyboard())
    await state.clear()


@scammer_router.message(AddScammerForm.get_profile)
async def get_scam(message: Message, bot: Bot, state: FSMContext):
    if message.user_shared:
        await get_scam_user(message, state)
    elif message.forward_from is not None:
        await message.answer(f"Вы переслали сообщение от {message.forward_from.first_name}: {message.text}")
        await message.answer("Мошшеник был добавлен в базу ✅", reply_markup=get_main_menu_keyboard())
        scammer = ScammerScheme(**message.forward_from.model_dump())
        await scammers_service.add_scammer(scammer)
        await state.clear()
    else:
        await message.answer(
            "Пользователь либо скрыл данные о себе, либо вы отправили что-то не то \n\n"
            "Отправьте его контакт с помощью кнопки ниже 👇👇👇",
            reply_markup=get_send_user_keyboard()
        )


@scammer_router.message(AddScammerForm.detect_hide_profile)
async def get_scam_user(message: Message, state: FSMContext):
    await message.answer("Мошенник был добавлен в базу ✅", reply_markup=get_main_menu_keyboard())
    data = {"id": message.user_shared.user_id}
    await scammers_service.add_scammer(ScammerScheme(**data))
    await state.clear()


# @scammer_router.message_handler(state=Form.age)
# async def process_age(message: types.Message, state: Form):
#     async with state.proxy() as data:
#         data['age'] = message.text
#     await message.reply("Из какого ты города?")
#     await Form.city.set()  # Устанавливаем состояние 'city'
#
#
# @scammer_router.message_handler(state=Form.city)
# async def process_city(message: types.Message, state: Form):
#     async with state.proxy() as data:
#         data['city'] = message.text
#
#         # Все данные собраны, можно завершить состояние FSM
#         # Здесь можно обработать данные или отправить их куда-то еще
#         await message.reply(f"Спасибо! Вот что я узнал: "
#                             f"Тебя зовут {data['name']}, тебе {data['age']} лет и ты из города {data['city']}")
#         # Сбрасываем состояние FSM после завершения обработки данных
#         await state.finish()
