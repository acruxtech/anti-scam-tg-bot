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

    info_about_scammer = ""
    if scammer:
        is_channel = "-100" in str(scammer.id)

        proof = await proof_repository.get_by_scammer_id(scammer.id)
        print("proof -", proof)

        info_about_scammer = f"<b>Информация о {'канале' if is_channel else 'пользователе'}:</b>\n\n"
        info_about_scammer += f"ID = <code>{scammer.id}</code>\n"

        if not is_channel:
            info_about_scammer += f"Для открытия профиля мошенника воспользуйтесь одной из ссылок (могут не работать из-за ограничений телеграма)\n"
            info_about_scammer += f"<a href='https://t.me/@id{scammer.id}'>Вечная ссылка 1</a>\n"
            info_about_scammer += f"<a href='tg://openmessage?user_id={scammer.id}'>Вечная ссылка 2</a>\n"
            info_about_scammer += f"tg://user?id={scammer.id}\n"

        print(info_about_scammer)

        if is_channel:
            scammer_message = "Этот канал - мошеннический!   ❌"
        else:       
            scammer_message = "Этот пользователь - мошенник!   ❌"
        if scammer.username:
            info_about_scammer += f"\n\nUsername = @{scammer.username}"

        if scammer.first_name:
            info_about_scammer += f"\n\nFirst Name = <code>{scammer.first_name}</code>"

        # исключения!!!
        if scammer.id == 612761675:
            scammer_message = scammer_message.replace("мошенник!", "очернитель!", 1)
            info_about_scammer = info_about_scammer.replace("профиля мошенника", "профиля очернителя", 1)
    else:
        scammer_message = "Данный пользователь не был найден в базе, но будьте осторожны"

    msg = (f"{scammer_message}\n\n"
          f"{info_about_scammer}")

    return proof, msg
