from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils import states, database
from config import developers, TOKEN, channel
from keyboards import client_kb

formClient = states.Client

base = database.DataBase()

client = Bot(TOKEN, parse_mode='HTML')

chat_members = ['LEFT', 'KICKED', 'RESTRICTED', 'BANNED'] # массив статусов для проверки пользователя

router = Router()

@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    check_member = await client.get_chat_member(chat_id=channel, user_id=message.from_user.id)

    if str(check_member.status).split('.')[-1] == "KICKED":
        return

    if str(check_member.status).split('.')[-1] in chat_members:
        return await message.answer('Вы не подписаны на канал❗\n\nДля того чтобы оставить объявление, необходимо быть подписанным на <a href="https://t.me/NaidiMeniaMckKtits">канал</a>.')
    
    await state.set_state(formClient.ptype)
    await message.answer('<b>👋 Здравствуйте!</b>\n\n<b>В данном боте вы можете предложить <i>свое объявление</i>, но оно будет опубликовано только при соблюдении <u>ряда правил</u>:</b>\n\n1️⃣ <b> Пост может содержать только <u>ОДНУ</u> фотографию или видео <u>НЕ БОЛЬШЕ 20 СЕКУНД</u></b>\n(не добавляйте больше одного фото или видео)\n\n<b>✅ Выберите тип объявления</b>', reply_markup=client_kb.choose_type())


@router.message(formClient.ptype)
@router.callback_query(client_kb.Postination.filter()) # лютая функция обработки колбэка клавиатуры
async def choose_post(query: CallbackQuery, callback_data: client_kb.Postination, state: FSMContext):
    if callback_data.action == "valentine":
        action = "#валентин"
        await query.message.delete_reply_markup()
        await query.message.edit_text("<b>Какое место для вас наилучшее, чтобы отпраздновать день всех влюбленных</b>")
        await state.update_data(
            userid=query.from_user.id,
            post_type=action,
            media=[]
        )
        await query.answer()
        await state.set_state(formClient.array)
        return

    if callback_data.action == 'find':
        action = '#найди_меня'
    
    if callback_data.action == 'lost':
        action = '#потеряшка'


    if callback_data.action == 'tagless':
        action = ''
    
    await state.update_data(
        userid=query.from_user.id,
        post_type=action,
        media=[]
    )
    await query.message.delete_reply_markup()
    await query.message.edit_text('<b>📎 Прикрепите одно или несколько фото и текст объявления\n( ТЕКСТ отправлять <i>ОТДЕЛЬНО</i>, максимальное количество фото - 3 )\n\n⚠️ Если вы хотите выбрать другую опцию отправки,\nнапишите /start для перезапуска бота</b>')
    await query.answer()
    await state.set_state(formClient.array)


@router.message(formClient.array)
async def form_name(message: Message, state: FSMContext):

    data = await state.get_data()
    photos = data['media']

    if data['post_type'] == "#валентин":
        await base.add_valentine(data['userid'], message.text)
        await state.clear()
        return await message.answer("нихуя нихуя. валя пошел")
        

    if photos and message.text:
        await state.update_data(
            description=message.text
        )
        await message.answer('Выберите опцию отправки:', reply_markup=client_kb.anonim())
        return await state.set_state(formClient.anon)
    
    if message.text:
        await state.update_data(
            description=message.text,
            media=None
        )
        await message.answer('Выберите опцию отправки:', reply_markup=client_kb.anonim())
        return await state.set_state(formClient.anon)

    if len(photos) >= 3:
        return await message.answer('<b>‼️ Максимальное кол-во фото - <i>3</i>.</b>\n\nТеперь введите текст объявления')
    
    photos.append(message.photo[-1].file_id)
    await state.update_data(
        media = photos
    )


@router.message(formClient.anon)
@router.callback_query(client_kb.Anonimation.filter())
async def choose_anon(query: CallbackQuery, callback_data: client_kb.Anonimation, state: FSMContext):

    succes_message = '<b>✅ Спасибо!</b>\n\nЕсли вы <b><u>корректно</u></b> предложили объявление, то, после модерации ваше объявление будет опубликовано.\nМодерация занимает до <b><i>12 часов</i></b>.\n\n<b>Список самых распространенных ошибок:</b>\n\n1️⃣ Вы предлагаете коммерческий пост\n2️⃣ Ваш пост не соответствует тематике канала\n3️⃣ Ваш пост неадекватный или содержит негативный подтекст\n\nТеперь вы знаете о всевозможных ошибках. Исправьте ошибки и предложите пост еще раз👍\n\n<b>Чтобы выложить еще одно объявления, нажмите /start</b>'
    error_message = '<b>⛔ При отправке объявления произошла ошибка!</b>\n\nНельзя опубликовать объявление <b><u>публично</u></b> без юзернейма!\nУстановить его можно <b><i>настройках профиля</i></b>'
    notify_message = '<b>🛎️ Новое объявление!</b>\n\n<b>Введите <i>/pending</i> чтобы посмотреть весь список обрабатывающихся объявлений.</b>'

    data = await state.get_data()

    if callback_data.action == 'otkat':
        await state.clear()
        await query.message.delete_reply_markup()
        await query.answer()
        return await query.message.answer('⚠️ Отправка объявления отменена')

    if callback_data.action == 'anon':
        await base.create_ticket(data=data, username='аноним')
        await query.message.delete_reply_markup()
        await query.message.edit_text(succes_message)
        await query.answer()
        list = await base.get_admins()
        for admin_id in list:
            await client.send_message(chat_id=admin_id, text=notify_message)
        return await state.clear()
    
    if not query.from_user.username:
        await query.message.delete_reply_markup()
        await query.message.edit_text(error_message)
        await query.answer()
        return await state.clear()
    
    await base.create_ticket(data=data, username=query.from_user.username)
    await query.message.delete_reply_markup()
    await query.message.edit_text(succes_message)
    await query.answer()
    list = await base.get_admins()
    for admin_id in list:
        await client.send_message(chat_id=admin_id, text=notify_message)
    await state.clear()