from aiogram import Bot, Router, F
from aiogram.types import Message

from src.config import OWNER_IDS

from src.entities.scammers.schemas import ScammerScheme
from src.entities.scammers.service import scammers_service
from src.entities.scammers.models import proof_repository

router = Router()

F: Message


@router.message(F.text.startswith("/add"))
async def add_quickly_scammer(message: Message):
    if message.from_user.id not in OWNER_IDS:
        return

    data = message.text.split(" ")
    print(data)

    scammer_id, proof_text = 0, ""

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

    await proof_repository.create(
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
