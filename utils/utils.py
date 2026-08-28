from asyncio import sleep
from difflib import get_close_matches

from aiogram.exceptions import TelegramNetworkError

from db.adler import TypeCompany
from utils.file import region_adler
from utils.file import region_gatter
from utils.gen_excel import CANONICAL_CITIES


def find_company_and_code(filename: str):
    if "Адлер" in filename or "Adler" in filename:
        for r, code in region_adler["Adler"].items():
            if r in filename:
                return TypeCompany.ADLER, r, code  # добавили r — сам регион

    if "Gatter" in filename or "Гаттер" in filename:
        for r, code in region_gatter["Gatter"].items():
            if r in filename:
                return TypeCompany.GATTER, r, code

    return None, None, None


async def safe_answer(message, text, retries=3):
    for i in range(retries):
        try:
            await message.answer(text)
            return
        except TelegramNetworkError:
            if i < retries - 1:
                await sleep(1)


def normalize_city(raw: str, threshold: float = 0.6) -> str | None:
    raw = raw.strip()
    matches = get_close_matches(raw, CANONICAL_CITIES, n=1, cutoff=threshold)
    return matches[0] if matches else None

