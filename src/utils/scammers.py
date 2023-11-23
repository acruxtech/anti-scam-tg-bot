from aiogram.types import Message

from src.entities.scammers.schemas import ScammerScheme


def get_scammer_data_from_message(message: Message) -> ScammerScheme:
    if message.forward_from:
        return ScammerScheme(**message.forward_from.model_dump())
    elif message.user_shared:
        data = {
            "id": message.user_shared.user_id
        }
        return ScammerScheme(**data)
