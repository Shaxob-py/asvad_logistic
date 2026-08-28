import re

from db.adler import GroupEntry, TypeCompany
from utils.gen_excel import CANONICAL_CITIES
from utils.utils import normalize_city

LINE_RE = re.compile(
    r'^(?P<region>[А-Яа-яЁё]+)\s+(?P<amount>[\d\s]+?)\s+(?P<code>[IH])$'
)


def parse_inkassatsiya_message(text: str):
    entries = []
    errors = []

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        match = LINE_RE.match(line)
        if not match:
            errors.append(f"Format mos kelmadi: {line!r}")
            continue

        region = match.group("region")
        amount_raw = match.group("amount")

        region = normalize_city(region)

        if region not in CANONICAL_CITIES:
            errors.append(f"Noma'lum region: {region!r} (qator: {line!r})")
            continue

        amount = int(amount_raw.replace(" ", ""))

        entries.append({
            "region": region,
            "amount": amount,
        })

    if len(entries) != 13:
        errors.append(f"Kutilgan 13 ta qator, topildi {len(entries)} ta")

    return entries, errors


import re
from datetime import datetime


async def parse_record(text: str):
    pattern = r'^(\d{2})-(\d{2})-(\d{4})\s+(.+?)\s+([\d\s]+)\s+(\S+)$'
    match = re.match(pattern, text.strip())

    if not match:
        raise ValueError(f'Не удалось распознать строку: {text}')

    day, month, year, city, raw_amount, currency = match.groups()

    await GroupEntry.create(region=normalize_city(city), date=datetime.today().date(),
                            inkassatsiya_amount=int(raw_amount.replace(" ", "")),
                            company=TypeCompany.GATTER)
