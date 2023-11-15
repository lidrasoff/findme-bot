from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, InputMedia, InputMediaDocument
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from utils import states, database
from main import client
from config import developers, channel
from keyboards import admin_kb

formAdmin = states.Admin

base = database.DataBase()

router = Router()


@router.message(Command('pending')) # получение списка обрабатываемых постов
async def get_pending(message: Message):
    if message.from_user.id not in developers: # проверка на доступ к админке в боте. Смотреть config
        return
    
    tickets = await base.get_tickets(message=message, status='pending') # в переменную tickets помещается готовый список, который получаем из БД. Смотреть database
    await message.answer(f'Список обрабатывающихся объявлений:\n\n{tickets}')


@router.message(Command('tickets')) # получение списка ВСЕХ постов в БД
async def get_all(message: Message):
    if message.from_user.id not in developers: # проверка на доступ к админке в боте. Смотреть config
        return
    
    tickets = await base.get_tickets(message=message, status=None) # в переменную tickets помещается готовый список, который получаем из БД. Смотреть database
    await message.answer(f'Список объявлений:\n\n{tickets}')


@router.message(Command('cancel')) # Выход из машины состояний || На всякий случай
async def cancel(message: Message, state: FSMContext):
    if message.from_user.id not in developers: # проверка на доступ к админке в боте. Смотреть config
        return
    await state.clear() # выход из машины состояний


@router.message(Command('select'))
async def select(message: Message, command: CommandObject, state: FSMContext):
    if message.from_user.id not in developers: # проверка на доступ к админке в боте. Смотреть config
        return
    
    ticketID = int(command.args.split()[0]) # берем первое значение из пользовательского ввода и преобразуем в int, если ввод будет некорректным - бот выдаст ошибку
    ticket = await base.get_ticket(ticketID=ticketID) # выполняем запрос в БД по полученному ticket_id


    if ticket['media'] == None: # проверка на наличие медиа-файла в посте
        await state.update_data(
            ticket_id = ticketID,
            media = None,
            description = ticket['description'],
            username = ticket['username'],
            post_type = ticket['type']
        ) # запись данных из БД в машину состояний (ВАЖНО)

        return await message.answer(f'{ticket["description"]}\n\nОтправитель: @{ticket["username"]}\n\n#{ticket["type"]}', reply_markup=admin_kb.confirmator()) # вывод поста с клавиатурой (опубликовать/отклонить)


    await state.update_data(
        ticket_id = ticketID,
        media = ticket['media'],
        description = ticket['description'],
        username = ticket['username'],
        post_type = ticket['type'],
        video = ticket['video']
    ) # запись данных из БД в машину состояний (ВАЖНО)

    if ticket['video'] == True: # проверка на тип медиа-файла. Видео-файл в данном случае
        return await message.answer_video(video=ticket["media"], caption=f'{ticket["description"]}\n\nОтправитель: @{ticket["username"]}\n\n#{ticket["type"]}', reply_markup=admin_kb.confirmator()) # вывод поста с клавиатурой (опубликовать/отклонить)

    await message.answer_photo(photo=ticket["media"], caption=f'{ticket["description"]}\n\nОтправитель: @{ticket["username"]}\n\n#{ticket["type"]}', reply_markup=admin_kb.confirmator()) # будет выводится, если тип медиа-файла это фотография
    


@router.callback_query(admin_kb.Confirmation.filter()) # лютая функция клавиатуры (опубликовать/отклонить)
async def choose_ticket(query: CallbackQuery, callback_data: admin_kb.Confirmation, state: FSMContext):
    data = await state.get_data() # получаем данные из МАШИНЫ СОСТОЯНИЙ, которые записали ранее

    if callback_data.action == 'decline': # будет выполняться если нажата кнопка отклонения. Смотреть тут: keyboards/admin_kb
        await base.remove_ticket(ticketID=data['ticket_id']) # запрос на удаление поста из БД по ticketID. Смотреть тут: utils/database.py
        await query.message.delete_reply_markup() # удаление клавиатуры после нажатия на кнопку (в целях защиты от повторного нажатия)
        await query.answer('❌ Отклонено!') # завершение колбэка (ВАЖНО)
        return await state.clear() # сброс машины состояний (ВАЖНО)

    # в остальном объявление будет опубликовываться

    if data['media'] == None: # проверка на наличие медиа-файла в посте
        await client.send_message(chat_id=channel, text=f'{data["description"]}\n\nОтправитель: @{data["username"]}\n\n#{data["post_type"]}') # отправка поста в определенный канал по channel_id. Смотреть config.py
        await base.edit_ticket(ticketID=data['ticket_id']) # изменение статуса поста в БД на "Опубликован". Смотреть тут: utils/database.py
        await query.message.delete_reply_markup()
        await query.answer('✅ Опубликовано!') 
        return await state.clear()
    
    if data['video'] == True: # проверка на тип медиа-файла в посте. В данном случае видео
        await client.send_video(chat_id=channel, video=data['media'], caption=f'{data["description"]}\n\nОтправитель: @{data["username"]}\n\n#{data["post_type"]}') # отправка поста в определенный канал по channel_id. Смотреть config.py
        await base.edit_ticket(ticketID=data['ticket_id'])
        await query.message.delete_reply_markup()
        await query.answer('✅ Опубликовано!')
        return await state.clear()
    
    # отправка поста с фото

    await client.send_photo(chat_id=channel, photo=data['media'], caption=f'{data["description"]}\n\nОтправитель: @{data["username"]}\n\n#{data["post_type"]}')
    await base.edit_ticket(ticketID=data['ticket_id'])
    await query.message.delete_reply_markup()
    await query.answer('✅ Опубликовано!')
    await state.clear()
    
