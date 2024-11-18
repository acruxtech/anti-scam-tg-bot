from contextlib import suppress

from aiogram import Bot, Router, F
from aiogram.filters import and_f
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from src.entities.scammers.service import scammers_service
from src.filters.admin import IsAdmin
from src.states.admin import AdminForm, AddRef, DeleteRef
from src.utils.media import create_media
from src.utils.excel import create_list_scammer
from src.keyboards.admin import get_admin_inline_keyboard, get_apply_photos_inline_keyboard, get_back_inline_keyboard
from src.keyboards.basic import get_send_user_keyboard, get_main_menu_keyboard, get_apply_send_keyboard
from src.utils.scammers import get_scammer_data_from_message, create_message_about_scammer
from src.entities.users.models import user_repository
from src.entities.chats.service import chat_service
from src.entities.refs.service import ref_service
from src.entities.refs.schemas import RefScheme
from src.entities.scammers.schemas import ScammerScheme
from src.entities.scammers.schemas import ProofScheme
from src.entities.refs.models import Ref


router = Router()
F: Message


@router.message(F.text == "Назад")
async def back(message: Message, state: FSMContext):
    await message.answer("Возвращаю в главное меню...", reply_markup=get_main_menu_keyboard(message.from_user.id))
    await state.clear()


@router.message(and_f(F.text == "Зайти в админку  📊", IsAdmin()))
async def open_admin(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    await message.answer("Вы зашли в админку \n\n"  
                         "Выберите действие:", reply_markup=get_admin_inline_keyboard())


F: CallbackQuery


@router.callback_query(and_f(F.data == "admin", IsAdmin()))
async def open_admin(call: CallbackQuery, bot: Bot, state: FSMContext):
    await state.clear()
    await call.message.answer(
        "Вы зашли в админку \n\n"
        "Выберите действие:",
        reply_markup=get_admin_inline_keyboard()
    )
    await call.answer()


@router.callback_query(and_f(F.data == "get_count_users", IsAdmin()))
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


@router.callback_query(and_f(F.data == "get_scammer_list", IsAdmin()))
async def get_list_scammer(call: CallbackQuery, bot: Bot):
    await call.message.answer("Отправляю весь список мошенников...")
    filename = await create_list_scammer()
    document = FSInputFile(path=filename)
    await bot.send_document(call.message.chat.id, document)
    await call.answer("Список отправлен")


@router.callback_query(and_f(F.data == "add_scammer", IsAdmin()))
async def start_add_scammer(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.answer(
        "Перешлите сообщение мошенника или отправьте его ид или отправьте профиль кнопкой ниже 👇👇👇",
        reply_markup=get_send_user_keyboard()
    )
    await state.set_state(AdminForm.get_user)
    await call.answer()


@router.callback_query(and_f(F.data == "delete_scammer", IsAdmin()))
async def start_delete_scammer(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.answer(
        "Отправьте ID мошенника (или перешлите сообщение, или отправьте контакт 👇👇👇",
        reply_markup=get_send_user_keyboard()
    )
    await state.set_state(AdminForm.delete_user)


F: Message


@router.message(and_f(AdminForm.delete_user, IsAdmin()))
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


@router.message(and_f(AdminForm.get_user, IsAdmin()))
async def get_user(message: Message, bot: Bot, state: FSMContext):
    if (
        message.user_shared or
        message.forward_from is not None and message.forward_from.id != message.from_user.id or
        (message.text and message.text.isdigit())
    ):
        await message.answer("Профиль мошенника получен  ✅", reply_markup=get_main_menu_keyboard(message.from_user.id))
        await message.answer("Напишите username мошенника:")
        scammer = get_scammer_data_from_message(message)
        await state.update_data(scammer=scammer)
        await state.set_state(AdminForm.get_username)
    else:
        await message.answer("Пользователь либо скрыл данные о себе, либо вы скинули что-то не то \n\n"
                             "Попробуйте отправить пользователя кнопкной ниже 👇👇👇")


@router.message(and_f(AdminForm.get_username, IsAdmin()))
async def get_username(message: Message, state: FSMContext):
    if message.text:
        data = await state.get_data()
        scammer = data["scammer"]
        scammer.username = message.text.replace("https://t.me/", "").replace("@", "")
        await state.update_data(scammer=scammer)
        await message.answer("Username мошенника получен  ✅")
        await message.answer("Отправьте пруфы и нажмите на кнопку", reply_markup=get_apply_photos_inline_keyboard())
        await state.set_state(AdminForm.get_proofs)
        await state.update_data(media=[])
    else:
        await message.answer("Пожалуйста, отправьте корректный username")


@router.message(and_f(AdminForm.get_proofs, IsAdmin()))
async def get_proofs(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()

    if message.photo:
        data["type"] = "photo"
        data["media"].append(max(message.photo, key=lambda x: x.height).file_id)
    if message.video:
        data["type"] = "video"
        data["media"].append(message.video[-1].file_id)
    await state.set_data(data)


@router.callback_query(and_f(AdminForm.get_proofs, IsAdmin()))
async def apply_proofs(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    if not data.get("media", None):
        data["media"] = []
        data["type"] = "only_text"
    await state.set_data(data)
    await call.answer()
    await call.message.answer("Отправьте причину, по которой мошенник заносится в базу")
    await state.set_state(AdminForm.get_reason)


@router.message(and_f(AdminForm.get_reason, IsAdmin()))
async def get_reason(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    scammer = data["scammer"]
    
    scammer_schema = ScammerScheme(
        id=scammer.id,
        username=scammer.username,
        first_name=scammer.first_name,
        language_code=scammer.language_code
    )
    proof_schema = ProofScheme(
        text=message.text, 
        scammer_id=scammer.id,
        user_id=message.from_user.id,
    )
    media_src = data["media"]
    media = []
    if data["type"] == "photo":
        for media_file_id in media_src:
            media.append({
                "file_id": media_file_id,
                "type": "photo",
                "scammer_id": scammer.id
            })
    if data["type"] == "video":
        for media_file_id in media_src:
            media.append({
                "file_id": media_file_id,
                "type": "video",
                "scammer_id": scammer.id
            })
    if data["type"] == "only_text":
        media = []

    scammer_created, proof = await scammers_service.save(scammer_schema, proof_schema, media, decision=True, moderator_id=message.from_user.id)
    await scammers_service.confirm(scammer_created.id)

    await message.answer("Подтвердите отправку по чатам", reply_markup=get_apply_send_keyboard(scammer.id))

    await state.clear()
    await message.answer("Мошенник добавлен в базу  ✅", reply_markup=get_main_menu_keyboard(message.from_user.id))


@router.callback_query(and_f(F.data.contains("apply_send"), IsAdmin()))
async def add_ref(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()

    scammer = await scammers_service.get_scammer(int(call.data.split("_")[-1]))
    chats = await chat_service.get_chats()
    for chat in chats:
        with suppress(BaseException):
            proof, msg = None, ""

            if scammer:
                proof, msg = await create_message_about_scammer(scammer)

            if proof:
                await create_media(scammer, proof, call.message, bot, msg, chat_id=chat.id, with_suffix=False)
    await call.message.answer("Скамер разослан по чатам")


@router.callback_query(and_f(F.data == "add_ref", IsAdmin()))
async def add_ref(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    await call.message.answer(
        "Отправьте название новой реф. ссылки (допустима только латиница)",
        reply_markup=get_back_inline_keyboard(),
    )
    await state.set_state(AddRef.here_title)


@router.message(and_f(AddRef.here_title, IsAdmin()))
async def add_ref_here_title(message: Message, bot: Bot, state: FSMContext):
    ref = RefScheme(title=message.text)
    await ref_service.add_ref(ref)
    await message.answer(f"Реф. ссылка успешно добавлена: https://t.me/{(await bot.get_me()).username}?start={message.text}")
    await state.clear()


@router.callback_query(and_f(F.data == "delete_ref", IsAdmin()))
async def delete_ref(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    await call.message.answer(
        "Отправьте порядковый номер реф. ссылки для удаления",
        reply_markup=get_back_inline_keyboard(),
    )
    await state.set_state(DeleteRef.here_number)


@router.message(and_f(DeleteRef.here_number, IsAdmin()))
async def delete_ref_here_number(message: Message, bot: Bot, state: FSMContext):
    await ref_service.delete_ref(int(message.text) - 1)
    await message.answer("Реф. ссылка успешно удалена")
    await state.clear()
