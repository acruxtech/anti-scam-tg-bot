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
    elif message.chat_shared:
        data = {
            "id": message.chat_shared.chat_id
        }
        return ScammerScheme(**data)


async def create_message_about_scammer(scammer):
    proof = None

    print("scammer -", scammer.is_scam)

    info_about_scammer = f"<b>Информация о пользователе:</b>\n\n"

    if scammer:
        proof = await proof_repository.get_by_scammer_id(scammer.id)
        print("proof -", proof)

        info_about_scammer += f"ID = <code>{scammer.id}</code>\n"
        info_about_scammer += f"Для открытия профиля мошенника воспользуйтесь одной из ссылок (могут не работать из-за ограничений телеграма)\n"
        info_about_scammer += f"tg://user?id={scammer.id}\n"
        info_about_scammer += f"https://t.me/@id{scammer.id}\n"
        info_about_scammer += f"tg://openmessage?user_id={scammer.id}\n"

        scammer_message = "Этот пользователь - мошенник!   ❌"
        if scammer.username:
            info_about_scammer += f"\n\nUsername = @{scammer.username}"

        if scammer.first_name:
            info_about_scammer += f"\n\nFirst Name = <code>{scammer.first_name}</code>"
    else:
        scammer_message = "Данный пользователь не был найден в базе, но будьте осторожны"

    msg = (f"{scammer_message}\n\n"
          f"{info_about_scammer}")

    return proof, msg
