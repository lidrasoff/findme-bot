from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.filters.callback_data import CallbackData

class Confirmation(CallbackData, prefix='con'): # создание класса для обработки колбэка инлайн-кнопок
    action: str

def confirmator(): # функция создания инлайн-кнопок
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='✅', callback_data=Confirmation(action='accept').pack()),
        InlineKeyboardButton(text='❌', callback_data=Confirmation(action='decline').pack()),
        InlineKeyboardButton(text='🚷', callback_data=Confirmation(action='ban').pack()),
        InlineKeyboardButton(text='❎', callback_data=Confirmation(action='clear_all').pack()),
        width=2 # этот параметр отвечает за кол-во кнопок в одном столбце
    )
    return builder.as_markup() # возвращаем инлайн-клавиатуру