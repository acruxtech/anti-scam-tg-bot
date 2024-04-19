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
from src.entities.users.models import user_repository
from src.entities.refs.service import ref_service
from src.entities.refs.schemas import RefScheme
from src.entities.scammers.schemas import ScammerScheme
from src.entities.scammers.schemas import ProofScheme
from src.entities.refs.models import Ref


class AdminForm(StatesGroup):
    get_user = State()
    get_username = State()
    get_proofs = State()
    delete_user = State()


class AddRef(StatesGroup):
    here_title = State()


class DeleteRef(StatesGroup):
    here_number = State()


router = Router()


F: Message


@router.message(F.text == "Назад")
async def back(message: Message, state: FSMContext):
    await message.answer("Возвращаю в главное меню...", reply_markup=get_main_menu_keyboard(message.from_user.id))
    await state.clear()


@router.message(F.text == "Зайти в админку  📊")
async def open_admin(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await message.answer("Вы зашли в админку \n\n"
                         "Выберите действие:", reply_markup=get_admin_inline_keyboard())


F: CallbackQuery


@router.callback_query(F.data == "get_count_users")
async def get_count_users(call: CallbackQuery, bot: Bot):
    count, count24, blocked_count, active_count = await user_repository.count_users()
    text = f"Количество пользователей - {count}\n"
    text += f"◾Живых: {active_count}\n"
    text += f"◾Мертвых: {blocked_count}\n\n"
    text += f"Количество новых пользователей за сутки - {count24}\n\n"

    refs: list[Ref] = await ref_service.get_refs()
    if refs:
        text += "Реф. ссылки:\n"
    text += "\n".join(f"{i + 1}. <code>{ref.title}</code> - {len(ref.users)} чел." for i, ref in enumerate(refs))
    
    await call.message.answer(text, parse_mode="html")
    await call.answer()


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
    data = await state.get_data()
    scammer = data["scammer"]
    if message.text:
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
        if not message.caption:
            return await message.answer("Отправьте причину добавления мошенника в подписи под медиа")
        scammer_schema = ScammerScheme(
            id=scammer.id,
            username=scammer.username,
            first_name=scammer.first_name,
            language_code=scammer.language_code
        )
        proof_schema = ProofScheme(
            text=message.caption, 
            scammer_id=scammer.id,
            user_id=message.from_user.id,
        )
        media = []
        if message.photo:
            for media_item in message.photo:
                media.append({
                    "file_id": media_item.file_id,
                    "type": "photo",
                    "scammer_id": scammer.id
                })
        if message.video:
            for media_item in message.video:
                media.append({
                    "file_id": media_item.file_id,
                    "type": "video",
                    "scammer_id": scammer.id
                })
        scammer_created, proof = await scammers_service.save(scammer_schema, proof_schema, media, decision=True, moderator_id=message.from_user.id)    
        await scammers_service.confirm(scammer_created.id)
        await state.clear()
        await message.answer("Мошенник добавлен в базу  ✅", reply_markup=get_main_menu_keyboard(message.from_user.id))


@router.callback_query(F.data == "add_ref")
async def add_ref(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    await call.message.answer("Отправьте название новой реф. ссылки (допустима только латиница)")
    await state.set_state(AddRef.here_title)


@router.message(AddRef.here_title)
async def add_ref_here_title(message: Message, bot: Bot, state: FSMContext):
    ref = RefScheme(title=message.text)
    await ref_service.add_ref(ref)
    await message.answer(f"Реф. ссылка успешно добавлена: https://t.me/{(await bot.get_me()).username}?start={message.text}")
    await state.clear()


@router.callback_query(F.data == "delete_ref")
async def delete_ref(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    await call.message.answer("Отправьте порядковый номер реф. ссылки для удаления")
    await state.set_state(DeleteRef.here_number)


@router.message(DeleteRef.here_number)
async def delete_ref_here_number(message: Message, bot: Bot, state: FSMContext):
    await ref_service.delete_ref(int(message.text) - 1)
    await message.answer("Реф. ссылка успешно удалена")
    await state.clear()