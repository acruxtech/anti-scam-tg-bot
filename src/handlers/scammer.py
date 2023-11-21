from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from src.keyboards.basic import get_send_user_keyboard
from src.entities.scammers.schemas import ScammerScheme
from src.entities.scammers.models import scammers_repository

scammer_router = Router()


class AddScammerForm(StatesGroup):
    get_profile = State()
    add_profile = State()
    detect_hide_profile = State()
    add_scam_to_database = State()


@scammer_router.message(F.text == "Добавить мошенника  ✍")
async def send_scam_user(message: Message, bot: Bot, state: FSMContext):
    await message.answer(f"Перешли сообщение мошенника, чтобы я получил о нём информацию ")
    await state.set_state(AddScammerForm.get_profile)


@scammer_router.message(AddScammerForm.get_profile)
async def get_scam(message: Message, bot: Bot, state: FSMContext):
    if message.forward_from is not None:
        await message.answer(f"Вы переслали сообщение от {message.forward_from.first_name}: {message.text}")
        await message.answer("Мошшеник был добавлен в базу ✅")
        scammer = ScammerScheme(**message.forward_from.model_dump())
        await scammers_repository.create(scammer.model_dump())
        await state.clear()
    else:
        await message.answer(
            "Пользователь скрыл данные о себе, отправьте его контакт с помощью кнопки ниже 👇👇👇",
            reply_markup=get_send_user_keyboard()
        )
        await state.set_state(AddScammerForm.detect_hide_profile)


@scammer_router.message(AddScammerForm.detect_hide_profile)
async def get_scam_user(message: Message, state: FSMContext):
    await message.answer("Мошшеник был добавлен в базу ✅")
    data = {"id": message.user_shared.user_id}
    await scammers_repository.create(data)
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
