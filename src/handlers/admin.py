from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from src.entities.scammers.service import scammers_service
from src.utils.excel import create_list_scammer
from src.keyboards.admin import get_admin_inline_keyboard
from src.keyboards.basic import get_send_user_keyboard, get_main_menu_keyboard
from src.utils.scammers import get_scammer_data_from_message
from src.entities.scammers.models import proof_repository
from src.repository import IntegrityException


class AdminForm(StatesGroup):
    get_user = State()
    get_username = State()
    get_proofs = State()
    delete_user = State()


router = Router()


F: Message


@router.message(F.text == "Назад")
async def back(message: Message, state: FSMContext):
    await message.answer("Возвращаю в главное меню...", reply_markup=get_main_menu_keyboard(message.from_user.id))
    await state.clear()


@router.message(F.text == "Зайти в админку  📊")
async def open_admin(message: Message, bot: Bot):
    await message.answer("Вы зашли в админку \n\n"
                         "Выберите действие:", reply_markup=get_admin_inline_keyboard())


F: CallbackQuery


@router.callback_query(F.data == "get_scammer_list")
async def get_list_scammer(call: CallbackQuery, bot: Bot):
    await call.message.answer("Отправляю весь список мошенников...")
    filename = await create_list_scammer()
    document = FSInputFile(path=filename)
    await bot.send_document(call.message.chat.id, document)
    await call.answer("Список отправлен")


@router.callback_query(F.data == "add_scammer")
async def start_add_scammer(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.answer(
        "Перешлите сообщение мошенника или отправьте его кнопкой ниже 👇👇👇", reply_markup=get_send_user_keyboard()
    )
    await state.set_state(AdminForm.get_user)
    await call.answer()


@router.callback_query(F.data == "delete_scammer")
async def start_delete_scammer(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.answer(
        "Отправьте ID мошенника (или перешлите сообщение, или отправьте контакт 👇👇👇",
        reply_markup=get_send_user_keyboard()
    )
    await state.set_state(AdminForm.delete_user)


F: Message


@router.message(AdminForm.delete_user)
async def delete_user(message: Message, bot: Bot, state: FSMContext):
    try:
        scammer_id = int(message.text)
    except (TypeError, ValueError):
        if message.user_shared or (message.forward_from is not None and message.forward_from.id != message.from_user.id):
            scammer_deleted = await scammers_service.delete_scammer(
                message.user_shared.user_id if message.user_shared else message.forward_from.id
            )
            if scammer_deleted:
                await message.answer("Пользователь удалён из базы  ✅", reply_markup=get_main_menu_keyboard(
                    message.from_user.id
                ))
                await state.clear()
            else:
                await message.answer("Пользователя нет в базе  🚫")
        else:
            await message.answer(
                "Пользователь либо скрыл данные о себе, либо вы скинули что-то не то \n\n"
                "Отправьте его ID или попробуйте отправить пользователя кнопкной ниже 👇👇👇"
            )
    else:
        scammer_deleted = await scammers_service.delete_scammer(scammer_id)
        if scammer_deleted:
            await message.answer("Пользователь удалён из базы  ✅", reply_markup=get_main_menu_keyboard(
                message.from_user.id
            ))
            await state.clear()
        else:
            await message.answer("Пользователя нет в базе  🚫")


@router.message(AdminForm.get_user)
async def get_user(message: Message, bot: Bot, state: FSMContext):
    if message.user_shared or (message.forward_from is not None and message.forward_from.id != message.from_user.id):
        await message.answer("Профиль мошенника получен  ✅", reply_markup=get_main_menu_keyboard(message.from_user.id))
        await message.answer("Напишите username мошенника:")
        scammer = get_scammer_data_from_message(message)
        await state.update_data(scammer=scammer)
        await state.set_state(AdminForm.get_username)
    else:
        await message.answer("Пользователь либо скрыл данные о себе, либо вы скинули что-то не то \n\n"
                             "Попробуйте отправить пользователя кнопкной ниже 👇👇👇")


@router.message(AdminForm.get_username)
async def get_username(message: Message, state: FSMContext):
    if message.text:
        data = await state.get_data()
        scammer = data["scammer"]
        scammer.username = message.text.replace("https://t.me/", "").replace("@", "")
        await state.update_data(scammer=scammer)
        await message.answer("Username мошенника получен  ✅")
        await message.answer("Напишите причину, по которой мошенник заносится в базу:")
        await state.set_state(AdminForm.get_proofs)
    else:
        await message.answer("Пожалуйста, отправьте корректный username")


@router.message(AdminForm.get_proofs)
async def get_proofs(message: Message, bot: Bot, state: FSMContext):
    if message.text:
        data = await state.get_data()
        scammer = data["scammer"]
        scammer_created = await scammers_service.add_scammer(scammer)
        await scammers_service.confirm(scammer_created.id)
        await proof_repository.create({
            "scammer_id": scammer.id,
            "text": message.text,
            "user_id": message.from_user.id,
            "decision": True,
            "moderator_id": message.from_user.id
        })
        await scammers_service.confirm(scammer_created.id)
        await state.clear()
        await message.answer("Мошенник добавлен в базу  ✅", reply_markup=get_main_menu_keyboard(message.from_user.id))
    else:
        await message.answer("Напишите причину, по которой мошенник заносится в базу")
