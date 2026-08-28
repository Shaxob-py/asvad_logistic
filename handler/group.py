from datetime import datetime

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message

from core.core import settings, bot
from db.adler import GroupEntry, TypeCompany
from db.user import User, Report
from utils.parsing import parse_inkassatsiya_message, parse_record

router_group = Router()


@router_group.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}), F.photo)
async def group_handler(message: Message):
    if message.chat.id == settings.GROUP_CHAT_ID_ADLER:
        type_company = Report.TypeCompany.ADLER
    elif message.chat.id == settings.GROUP_CHAT_ID_GATTER:
        type_company = Report.TypeCompany.GATTER
    else:
        return
    user = await User.create_or_update(
        telegram_id=message.from_user.id,
        username=message.from_user.username or message.from_user.first_name,
    )

    await Report.create_report_for_user(user_id=user.id, type_company=type_company)


@router_group.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}), F.text)
async def group_handler(message: Message):
    if message.chat.id == settings.GROUP_CHAT_ID_ADLER:
        type_company = TypeCompany.ADLER
    elif message.chat.id == settings.GROUP_CHAT_ID_GATTER:
        type_company = TypeCompany.GATTER
    else:
        return
    entr, errors = parse_inkassatsiya_message(message.text)
    if errors:
        await bot.send_message(5121755384, "\n".join(errors))
        await parse_record(message.text)
        return
    for entry in entr:
        await GroupEntry.create(
            region=entry["region"],
            date=datetime.today().date(),
            inkassatsiya_amount=entry["amount"],
            company=type_company)
