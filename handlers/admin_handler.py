from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from utils import states, database
from main import client
from config import developers, channel
from keyboards import admin_kb

formAdmin = states.Admin

base = database.DataBase()

router = Router()


@router.message(Command('pending'))
async def get_pending(message: Message):
    if message.from_user.id not in developers:
        return
    
    tickets = await base.get_tickets(status='pending')

    await message.answer(f'Список обрабатывающихся объявлений:\n\n{tickets}')


@router.message(Command('tickets'))
async def get_all(message: Message):
    if message.from_user.id not in developers:
        return
    
    tickets = await base.get_tickets(status=None)
    await message.answer(f'Список объявлений:\n\n{tickets}')


@router.message(Command('cancel'))
async def cancel(message: Message, state: FSMContext):
    if message.from_user.id not in developers:
        return
    await state.clear()


@router.message(Command('select'))
async def select(message: Message, command: CommandObject, state: FSMContext):
    if message.from_user.id not in developers:
        return
    
    ticketID = int(command.args.split()[0])
    ticket = await base.get_ticket(ticketID=ticketID)


    if ticket['media'] == None:
        await state.update_data(
            ticket_id=ticketID,
            media=None,
            description=ticket['description'],
            username=ticket['username'],
            post_type=ticket['type']
        )

        return await message.answer(f'{ticket["description"]}\n\nОтправитель: @{ticket["username"]}\n\n#{ticket["type"]}', reply_markup=admin_kb.confirmator())

    await state.update_data(
        ticket_id=ticketID,
        media=ticket['media'],
        description=ticket['description'],
        username=ticket['username'],
        post_type=ticket['type']
    )

    media_group = [InputMediaPhoto(media=file_id) for file_id in ticket['media']]

    await message.answer_media_group(media=media_group)
    await message.answer(f'{ticket["description"]}\n\nОтправитель: @{ticket["username"]}\n\n#{ticket["type"]}', reply_markup=admin_kb.confirmator())


@router.callback_query(admin_kb.Confirmation.filter())
async def choose_ticket(query: CallbackQuery, callback_data: admin_kb.Confirmation, state: FSMContext):
    data = await state.get_data()

    if callback_data.action == 'decline':
        await base.remove_ticket(ticketID=data['ticket_id'])
        await query.message.delete_reply_markup()
        await query.answer('❌ Отклонено!')
        return await state.clear()


    if data['media'] == None:
        await client.send_message(chat_id=channel, text=f'{data["description"]}\n\nОтправитель: @{data["username"]}\n\n#{data["post_type"]}')
        await base.edit_ticket(ticketID=data['ticket_id'])
        await query.message.delete_reply_markup()
        await query.answer('✅ Опубликовано!')
        return await state.clear()
    

    media_group = [InputMediaPhoto(media=file_id) for file_id in data['media']]
    media_group[0] = InputMediaPhoto(media=data['media'][0], caption=f'{data["description"]}\n\nОтправитель: @{data["username"]}\n\n#{data["post_type"]}')

    await client.send_media_group(chat_id=channel, media=media_group)
    await base.edit_ticket(ticketID=data['ticket_id'])
    await query.message.delete_reply_markup()
    await query.answer('✅ Опубликовано!')
    await state.clear()
    
