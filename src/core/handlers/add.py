from aiogram import Router, F
from aiogram.filters import and_f
from aiogram.types import Message

from src.core.schemas.scammer import ScammerScheme
from src.core.services.scammer import scammers_service
from src.db.models import Proof
from src.core.filters.admin import IsAdmin


router = Router()
F: Message


@router.message(and_f(F.text.startswith("/add"), IsAdmin()))
async def add_quickly_scammer(message: Message):
    data = message.text.split(" ")

    try:
        scammer_id, proof_text = int(data[1]), " ".join(data[2:])
    except (IndexError, ValueError):
        await message.answer(
            "Некорректные данные. Пример того, как пользоваться командой:\n\n"
            "/add 111222333 украл 10к"
        )
        return

    scammer_id_from_db = await scammers_service.add_scammer(ScammerScheme(
        id=scammer_id
    ))

    await scammers_service.confirm(scammer_id_from_db.id)

    # todo: вынести в proof_service
    await Proof.repository().create(
        {
            "text": proof_text,
            "scammer_id": scammer_id_from_db.id,
            "user_id": message.from_user.id,
            "moderator_id": message.from_user.id,
            "decision": True
        }
    )

    await message.answer(
        "Мошенник был добавлен в базу  ✅"
    )
