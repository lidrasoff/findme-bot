from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.filters.callback_data import CallbackData
from config import active_14


class Anonimation(CallbackData, prefix='ano'): # создание класса для обработки колбэка инлайн-кнопок
    action: str

def anonim(): # функция создания инлайн-кнопок
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='📢 Публично', callback_data=Anonimation(action='send').pack()),
        InlineKeyboardButton(text='😶‍🌫️ Анонимно', callback_data=Anonimation(action='anon').pack()),
        InlineKeyboardButton(text='🗑️ Отменить объявление', callback_data=Anonimation(action='otkat').pack()),
        width=1 # этот параметр отвечает за кол-во кнопок в одном столбце
    )
    return builder.as_markup() # возвращаем инлайн-клавиатуру


class Postination(CallbackData, prefix='post'):
    action: str

def choose_type():
    builder = InlineKeyboardBuilder()
    if active_14 == True:
        builder.row(
            InlineKeyboardButton(text='💘 14 Февраля', callback_data=Postination(action='valentine').pack()),
            InlineKeyboardButton(text='📸 Найди меня', callback_data=Postination(action='find').pack()),
            InlineKeyboardButton(text='🔎 Потеряшка', callback_data=Postination(action='lost').pack()),
            InlineKeyboardButton(text='✏️ Без тега', callback_data=Postination(action='tagless').pack()),
            
            width=1
        )
    else:
        builder.row(
            InlineKeyboardButton(text='📸 Найди меня', callback_data=Postination(action='find').pack()),
            InlineKeyboardButton(text='🔎 Потеряшка', callback_data=Postination(action='lost').pack()),
            InlineKeyboardButton(text='✏️ Без тега', callback_data=Postination(action='tagless').pack()),
            
            width=1
        )
    return builder.as_markup()