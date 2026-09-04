import asyncio
import datetime
from venv import logger

from aiogram import F, Router, BaseMiddleware
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile

from core.core import bot
from db.adler import Entry, GroupEntry
from utils.gen_excel import generate_summary_excel, get_inkassatsiya_row, generate_inkassatsiya_excel
from utils.key import reply_buttons
from utils.state import AdminState
from utils.utils import find_company_and_code, safe_answer, normalize_city

router_admin = Router()


# class AdminMiddleware(BaseMiddleware):
#     async def __call__(self, handler, event, data):
#         user_id = event.from_user.id
#
#         if user_id not in [5121755384]:
#             return
#
#         return await handler(event, data)
#
#
# router_admin.message.middleware(AdminMiddleware())


@router_admin.message(AdminState.get_document , F.text=="Orqaga ⬅️")
@router_admin.message(AdminState.get_date_for_excel , F.text=="Orqaga ⬅️")
@router_admin.message(AdminState.generate_excel , F.text=="Orqaga ⬅️")
@router_admin.message(Command("start"))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    button = ["Sverka Fin Otchet chiqarish", "Rashod Exel Kiritish", "Barcha inkasatsalar"]
    await message.answer("Assalomu alekum nima qilmoqchisiz", reply_markup=reply_buttons(button))
    await state.set_state()


@router_admin.message(F.document, AdminState.get_document)
async def command_register_admin(message: Message, state: FSMContext) -> None:
    try:
        doc = message.document

        file = await bot.get_file(doc.file_id)
        file_bytes_io = await bot.download_file(file.file_path)
        file_bytes = file_bytes_io.read()

        company_type, region, code = find_company_and_code(doc.file_name)

        if code is None:
            await message.answer(
                f"Bu fayl bilan hatolik yuz berdi: {doc.file_name}"
            )
            return

        data = await state.get_data()
        date_str = data.get("date")

        target_date = datetime.datetime.strptime(
            date_str,
            "%Y-%m-%d"
        ).date()

        region = normalize_city(region)


        group_entry = await GroupEntry.get_by_region_date(
            region,
            target_date,
            company_type
        )

        if group_entry is None:
            await message.answer("Bunday kun bazada yo'q")
            return

        if region == "Нукус":
            balance_before, amount, balance_after = await asyncio.to_thread(
                get_inkassatsiya_row,
                file_bytes,
                code,
                target_date,
                group_entry,
                date_col=0,
                statya_col=1,
                amount_col=5,
                balance_col=6
            )
        else:
            balance_before, amount, balance_after = await asyncio.to_thread(
                get_inkassatsiya_row,
                file_bytes,
                code,
                target_date,
                group_entry
            )

        await Entry.create_or_update(
            region=region,
            inkassatsiya_amount=amount,
            company=company_type,
            date=target_date,
            balance_before=balance_before,
            balance_after=balance_after
        )

    except TelegramNetworkError:
        await safe_answer(
            message,
            "Xatolik yuz berdi, qayta urinib ko'ring"
        )

    except Exception as e:
        await safe_answer(
            message,
            "Kutilmagan xatolik yuz berdi, qayta urinib ko'ring"
        )
        logger.exception(
            "command_register_admin failed: %s",
            e
        )


@router_admin.message(F.text == "Rashod Exel Kiritish", )
async def command__admin(message: Message, state: FSMContext) -> None:
    await message.answer("Qaysi kunni rashodini olishim kerak. Masalan -> Yil-oy-kun  shu formatta kiriting",reply_markup=reply_buttons(["Orqaga ⬅️"]))
    await state.set_state(AdminState.get_date_for_excel)


@router_admin.message(AdminState.get_date_for_excel)
async def command__admin(message: Message, state: FSMContext) -> None:
    await message.answer('Documentlarni yuboring')
    date = message.text
    await state.update_data(date=date)
    await state.set_state(AdminState.get_document)


@router_admin.message(F.text == "Sverka Fin Otchet chiqarish", )
async def command_fin_document(message: Message, state: FSMContext) -> None:
    await message.answer('Qaysi kunniki sverka fin otchet kerak.Masalan -> kun-oy-yil  shu formatta kiriting',reply_markup=reply_buttons(["Orqaga ⬅️"]))
    await state.set_state(AdminState.generate_excel)


@router_admin.message(AdminState.generate_excel)
async def command_generate_excel(message: Message, state: FSMContext) -> None:
    target_date = datetime.datetime.strptime(message.text, '%Y-%m-%d').date()

    entries = await Entry.select_months(target_date)

    generate_summary_excel(target_date, entries)
    excel_bytes = generate_summary_excel(target_date, entries)
    await message.answer_document(BufferedInputFile(excel_bytes, filename=f"summary_{target_date}.xlsx"))
    await state.clear()
    button = ["Sverka Fin Otchet chiqarish", "Rashod Exel Kiritish", "Barcha inkasatsalar"]
    await message.answer("Assalomu alekum nima qilmoqchisiz", reply_markup=reply_buttons(button))


@router_admin.message(F.text == "Barcha inkasatsalar")
async def get_check(message: Message, state: FSMContext) -> None:
    data = await GroupEntry.get_all()

    if not data:
        await message.answer("Inkasatsalar yo'q")
        return

    excel = generate_inkassatsiya_excel(data)

    await message.answer_document(
        BufferedInputFile(
            excel.read(),
            filename="inkassatsiyalar.xlsx"
        )
    )