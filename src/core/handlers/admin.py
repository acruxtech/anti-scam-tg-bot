import asyncio
from contextlib import suppress
from datetime import datetime

from aiogram import Bot, Router, F
from aiogram.exceptions import AiogramError
from aiogram.filters import and_f
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from pyrogram import Client

from src.config import API_ID, API_HASH
from src.core.services.scammer import scammers_service
from src.core.filters.admin import IsAdmin
from src.core.states.admin import AdminForm, AddRef, DeleteRef
from src.core.utils.media import create_media
from src.core.utils.excel import create_list_scammer
from src.core.keyboards.admin import (
    get_admin_inline_keyboard,
    get_apply_photos_inline_keyboard,
    get_back_inline_keyboard, get_mailing_keyboard, get_apply_mailing_keyboard
)
from src.core.keyboards.basic import get_send_user_keyboard, get_main_menu_keyboard, get_apply_send_keyboard
from src.core.utils.scammers import get_scammer_data_from_message, create_message_about_scammer
from src.core.services import ref_service, chat_service, user_service
from src.core.schemas import RefScheme, ScammerScheme, ProofScheme
from src.core.utils.variables import scheduler, bot
from src.db.models import Ref


router = Router()
F: Message


class Mailing(StatesGroup):
    here_time = State()
    forward_post = State()
    apply = State()


# @router.message()
# async def rvfecds(message: Message, state: FSMContext):
#     with open("edhsjk.json", "w", encoding="utf-8") as f:
#         print(message.__dict__, file=f)
#     await state.clear()
#     async with Client(
#             "session",
#             api_id=API_ID,
#             api_hash=API_HASH,
#     ) as client:
#         pass


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
    count, count24, blocked_count, active_count = await user_service.count_users()
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


F: CallbackQuery


@router.callback_query(and_f(F.data == "mailing", IsAdmin()))
async def mailing(callback: CallbackQuery):
    await callback.message.answer("Настройки рассылок", reply_markup=get_mailing_keyboard())
    await callback.answer()


@router.callback_query(and_f(F.data == "create_mailing", IsAdmin()))
async def create_mailing(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Отправьте время рассылки в формате YYYY.MM.DD HH:MM (например, 2024.10.31 12:00)",
    )
    await callback.answer()
    await state.set_state(Mailing.here_time.state)


@router.message(and_f(Mailing.here_time, IsAdmin()))
async def mailing_here_time(message: Message, state: FSMContext):
    data = {}
    try:
        data["date"] = datetime.strptime(message.text, "%Y.%m.%d %H:%M")
        await state.set_data(data)
    except BaseException as e:
        return await message.answer("Неправильный формат ввода! Попробуйте еще раз")

    await message.answer("Отправьте пост для рассылки")
    await state.set_state(Mailing.forward_post.state)


@router.message(and_f(Mailing.forward_post, IsAdmin()))
async def mailing_here_post(message: Message, state: FSMContext):
    data = await state.get_data()
    data["chat_id"] = message.chat.id
    data["msg_id"] = message.message_id

    if message.reply_markup:
        inline_keyboard_json = [
            [{"text": button.text, "url": button.url} for button in row]
            for row in message.reply_markup.inline_keyboard
        ]
    else:
        inline_keyboard_json = None

    data["reply_markup"] = inline_keyboard_json
    await state.set_data(data)

    await message.bot.copy_message(
        message.chat.id,
        message.chat.id,
        message.message_id,
        reply_markup=message.reply_markup,
    )

    await message.answer(
        f"Подтвердить запланирование рассылки на {data['date']}?",
        reply_markup=get_apply_mailing_keyboard()
    )
    await state.set_state(Mailing.apply.state)


@router.callback_query(and_f(F.data == "apply_mailing", Mailing.apply, IsAdmin()))
async def apply_mailing(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user_ids = await user_service.get_ids()
    filename = f"mailing_{data['date']}.txt"
    with open(filename, "w") as f:
        for user_id in user_ids:
            f.write(f"{user_id}\n")

    scheduler.add_job(
        send_messages,
        "date",
        kwargs={
            "chat_id": data["chat_id"],
            "msg_id": data["msg_id"],
            "reply_markup": data["reply_markup"],
            "filename": filename,
        },
        run_date=data["date"],
        misfire_grace_time=1000,
        coalesce=True,
    )

    await callback.message.answer("Рассылка запланирована")
    await callback.answer()
    await state.clear()


async def send_messages(chat_id: int, msg_id: int, reply_markup: list[list[dict]], filename: str):
    success = 0
    with_error = 0

    msg = await bot.send_message(
        chat_id,
        "Рассылка запущена\n"
        "Успешно: 0, неудачно: 0",
    )

    if reply_markup:
        inline_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=button["text"], url=button["url"]) for button in row]
                for row in reply_markup
            ]
        )
    else:
        inline_keyboard = None

    with open(filename, "r") as f:
        for user_id in f:
            try:
                user_id = int(user_id)

                await bot.copy_message(
                    user_id,
                    chat_id,
                    msg_id,
                    reply_markup=inline_keyboard
                )
                success += 1
                await asyncio.sleep(0.035)

            except AiogramError as e:
                ...
            except BaseException:
                with_error += 1

            finally:
                with suppress(BaseException):
                    if (success + with_error) % 100 == 0:
                        await msg.edit_text(
                            "Рассылка запущена\n"
                            f"Успешно: {success}, неудачно: {with_error}",
                        )

    with suppress(BaseException):
        await msg.edit_text(
            "Рассылка запущена\n"
            f"Успешно: {success}, неудачно: {with_error}"
        )
    await bot.send_message(
        chat_id,
        "Рассылка завершена"
    )


@router.callback_query(and_f(F.data.startswith("cancel_mailing"), IsAdmin()))
async def cancel_create_mailing(callback: CallbackQuery, state: FSMContext):
    mailing_id = callback.data.split("_")[-1]
    if mailing_id != "mailing":
        scheduler.remove_job(mailing_id)
    await callback.message.answer("Рассылка отменена")
    await callback.answer()
    await state.clear()


@router.callback_query(and_f(F.data == "delete_mailing", IsAdmin()))
async def cancel_mailing(callback: CallbackQuery):
    await callback.answer()
    buttons = [
        [
            InlineKeyboardButton(
                text=task.next_run_time.strftime("%Y.%m.%d %H:%M"),
                callback_data=f"cancel_mailing_{task.id}"
            )
        ]
        for task in scheduler.get_jobs()
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    keyboard.row_width = 1
    await callback.message.answer(
        "Выберите рассылку, которую надо удалить",
        reply_markup=keyboard,
    )


@router.callback_query(and_f(F.data == "export", IsAdmin()))
async def export(callback: CallbackQuery, state: FSMContext):
    with open("users.txt", "w") as f:
        users_ids = await user_service.get_ids()
        users_usernames = await user_service.get_usernames()
        for user_id, username in zip(users_ids, users_usernames):
            f.write(f"{user_id} @{username}\n")

    # with open("users.txt", "r") as f:
    await callback.message.answer_document(FSInputFile("users.txt"))

    await callback.answer()
    await state.clear()
