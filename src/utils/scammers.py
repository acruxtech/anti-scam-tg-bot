from aiogram.types import Message

from src.entities.scammers.models import proof_repository
from src.entities.scammers.schemas import ScammerScheme


def get_scammer_data_from_message(message: Message) -> ScammerScheme:
    if message.forward_from:
        return ScammerScheme(**message.forward_from.model_dump())
    elif message.user_shared:
        data = {
            "id": message.user_shared.user_id
        }
        return ScammerScheme(**data)


async def create_message_about_scammer(scammer, message: Message):
    proof = None

    info_about_scammer = f"<b>Информация о пользователе:</b>\n\n"

    if scammer and scammer.is_scam:
        proof = await proof_repository.get_by_scammer_id(scammer.id)

        info_about_scammer += f"ID = <code>{scammer.id}</code>"

        scammer_message = "Этот пользователь - мошенник!   ❌"
        if scammer.username:
            info_about_scammer += f"\n\nUsername = <code>{scammer.username}</code>"

        if scammer.first_name:
            info_about_scammer += f"\n\nFirst Name = <code>{scammer.first_name}</code>"
    else:
        scammer_message = "Данный пользователь не был найден в базе, но будьте осторожны"

    await message.answer(f"{scammer_message}\n\n"
                         f"{info_about_scammer}")

    return proof
