from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from src.config import TECH_SUPPORT_ID
from src.core.keyboards.menu import get_contact_answer
from src.core.keyboards.basic import get_contact_cancel_keyboard, get_main_menu_keyboard
from src.core.utils.callbacks import ContactMessage
from src.core.services import contact_message_service


class ContactState(StatesGroup):
    get_contact_text = State()
    get_text_for_contact = State()


router = Router()


F: Message


@router.message(F.text == "Связаться с нами  📞")
async def start_contact(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
        "Тут Вы можете задать любой вопрос по сервису, оставить отзыв или "
        "подсказать как сделать AntiSkamTG ещё полезнее!",
        reply_markup=get_contact_cancel_keyboard()
    )
    await state.set_state(ContactState.get_contact_text)


@router.message(ContactState.get_contact_text, F.text == "Назад")
async def back(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Возвращаю в главное меню...", reply_markup=get_main_menu_keyboard(message.from_user.id))
    await state.clear()


@router.message(ContactState.get_contact_text, F.text)
async def get_text_contact(message: Message, bot: Bot, state: FSMContext):
    links = [
        f"tg://user?id={message.from_user.id}", 
        f"https://t.me/@id{message.from_user.id}", 
        f"tg://openmessage?user_id={message.from_user.id}",
    ]
    await bot.send_message(
        TECH_SUPPORT_ID,
        text=f"Пришло сообщение от <b>@{message.from_user.username}</b>\n\n<b>Ссылки на профиль:</b>\n" + "\n".join(links)
    )
    contact_message = await contact_message_service.create_contact_message(message.from_user.id, message.text)
    await bot.send_message(
        TECH_SUPPORT_ID, text=f"<b>@{message.from_user.username}</b>: {message.text}",
        reply_markup=get_contact_answer(contact_message_id=contact_message.id)
    )
    await message.answer(
        "Спасибо за вопрос! Мы ответим на него как можно скорее!",
        reply_markup=get_main_menu_keyboard(message.from_user.id)
    )
    await state.clear()


F: CallbackQuery


@router.callback_query(ContactMessage.filter())
async def answer_to_contact(callback: CallbackQuery, callback_data: ContactMessage, state: FSMContext):
    await callback.message.answer("Напишите сообщению пользователю:")
    await state.update_data(contact_message_id=callback_data.id)
    await state.set_state(ContactState.get_text_for_contact)
    await callback.answer()

F: Message


@router.message(ContactState.get_text_for_contact, F.text)
async def send_message_to_contact(message: Message, bot: Bot, state: FSMContext):
    contact_data = await state.get_data()
    contact_message_id = contact_data["contact_message_id"]
    contact_message = await contact_message_service.answer_contact_message(
        contact_message_id, message.text, message.from_user.id
    )
    await message.answer("Ответ был отправлен пользователю  ✅")
    await bot.send_message(
        contact_message.contact_id, text=f"<b>Мы ответили на твой вопрос:</b> \n\n"
                                         f"<i>{contact_message.message}</i> \n\n"
                                         f"<b>Ответ от модератора:</b> \n\n"
                                         f"<i>{message.text}</i>",
        reply_markup=get_main_menu_keyboard(message.from_user.id)
    )
    await state.clear()
