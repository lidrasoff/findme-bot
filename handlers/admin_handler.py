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

@router.message(Command('add_admin'))
async def add_new(message: Message, command: CommandObject):
    level = await base.get_level(message.from_user.id)
    print(level)
    list = await base.get_admins()
    if message.from_user.id not in list:
        return
    if int(level[0]) < 2:
        return
    
    admin_id = int(command.args.split()[0])
    lvl = int(command.args.split()[1])

    if int(level[0]) <= lvl:
        return await message.answer("Уровень админа не может быть выше вашего!")
    if admin_id in developers:
        return await message.answer("Админ разработчик.")
    if lvl == 0:
        return await base.del_admin(admin_id)
    await base.add_admin(admin_id, lvl)

@router.message(Command('pending'))
async def get_pending(message: Message):
    list = await base.get_admins()
    if message.from_user.id not in list:
        return
    
    tickets = await base.get_tickets(status='pending')

    await message.answer(f'Список обрабатывающихся объявлений:\n\n{tickets}')


@router.message(Command('tickets'))
async def get_all(message: Message):
    list = await base.get_admins()
    if message.from_user.id not in list:
        return
    
    tickets = await base.get_tickets(status=None)
    await message.answer(f'Список объявлений:\n\n{tickets}')


@router.message(Command('cancel'))
async def cancel(message: Message, state: FSMContext):
    list = await base.get_admins()
    if message.from_user.id not in list:
        return
    await state.clear()


@router.message(Command('select'))
async def select(message: Message, command: CommandObject, state: FSMContext):
    list = await base.get_admins()
    if message.from_user.id not in list:
        return
    
    ticketID = int(command.args.split()[0])
    try:
        ticket = await base.get_ticket(ticketID=ticketID)
    except IndexError:
        await message.answer('❌Ошибка! Объявление не найдено!')
    except ValueError:
        await message.answer('❌Ошибка! ID объявления должен быть целым числом!')

    if ticket['media'] == None:
        await state.update_data(
            ticket_id=ticketID,
            media=None,
            description=ticket['description'],
            username=ticket['username'],
            id=ticket['user_id'],
            post_type=ticket['type']
        )

        return await message.answer(f'{ticket["description"]}\n\nОтправитель: @{ticket["username"]}\n\n{ticket["type"]}', parse_mode=None, reply_markup=admin_kb.confirmator())

    await state.update_data(
        ticket_id=ticketID,
        media=ticket['media'],
        description=ticket['description'],
        username=ticket['username'],
        id=ticket['user_id'],
        post_type=ticket['type']
    )

    media_group = [InputMediaPhoto(media=file_id) for file_id in ticket['media']]

    await message.answer_media_group(media=media_group)
    await message.answer(f'{ticket["description"]}\n\nОтправитель: @{ticket["username"]}\n\n{ticket["type"]}', reply_markup=admin_kb.confirmator())


@router.callback_query(admin_kb.Confirmation.filter())
async def choose_ticket(query: CallbackQuery, callback_data: admin_kb.Confirmation, state: FSMContext):
    data = await state.get_data()

    if callback_data.action == 'decline':
        await base.remove_ticket(ticketID=data['ticket_id'])
        await query.message.delete_reply_markup()
        await query.answer('❌ Отклонено!')
        return await state.clear()
    if callback_data.action == "ban":
        await client.ban_chat_member(chat_id=channel, user_id=data['id'])
        await query.message.delete_reply_markup()
        await query.answer("🚷Пользователь забанен!")
        return await state.clear()
    if callback_data.action == "clear_all":
        await base.remove_all_tickets(userid=data['id'])
        await query.message.delete_reply_markup()
        await query.answer("❎Все сообщения от пользователя удалены!")
        return await state.clear()


    if data['media'] == None:
        await client.send_message(chat_id=channel, text=f'{data["description"]}\n\nОтправитель: @{data["username"]}\n\nВыложить объвление:\n— @vadimblyatbot\n\n{data["post_type"]}', parse_mode=None)
        await base.edit_ticket(ticketID=data['ticket_id'])
        await query.message.delete_reply_markup()
        await query.answer('✅ Опубликовано!')
        return await state.clear()
    

    media_group = [InputMediaPhoto(media=file_id) for file_id in data['media']]
    media_group[0] = InputMediaPhoto(media=data['media'][0], caption=f'{data["description"]}\n\nОтправитель: @{data["username"]}\n\nВыложить объвление:\n— @vadimblyatbot\n\n{data["post_type"]}', parse_mode=None)

    await client.send_media_group(chat_id=channel, media=media_group)
    await base.edit_ticket(ticketID=data['ticket_id'])
    await query.message.delete_reply_markup()
    await query.answer('✅ Опубликовано!')
    await state.clear()

