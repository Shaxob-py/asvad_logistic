from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def reply_buttons(button: list):
    rkb = ReplyKeyboardBuilder()
    for button in button:
        rkb.add(KeyboardButton(text=button))


    rkb.adjust(3)
    return rkb.as_markup(resize_keyboard=True)
