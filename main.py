import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message , BotCommand, BotCommandScopeChat, BotCommandScopeAllChatAdministrators

from handlers import admin_handler, client_handler
from utils import database
from config import developers, TOKEN

base = database.DataBase()

client = Bot(TOKEN, parse_mode='HTML')

async def main():
    client = Bot(TOKEN, parse_mode='HTML')
    dp = Dispatcher()

    dp.include_routers(
        client_handler.router,
        admin_handler.router
    )

    print('Стартуем')
    
    await base.create_table()

    await client.set_my_commands(commands=[
        BotCommand(command='start', description='Создать объявление'),
    ])

    for developer in developers:
        await client.set_my_commands(commands=[
            BotCommand(command='start', description='Создать объявление'),
            BotCommand(command='pending', description='Список обрабатываемых объявлений'),
            BotCommand(command='tickets', description='Список всех объявлений'),
            BotCommand(command='select', description='Выбрать объявление'),
            BotCommand(command='cancel', description='Отменить действие'),
    ], scope=BotCommandScopeChat(chat_id=developer)) # установка доп списка команд модераторам. Смотреть config.py

    await client.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(client)



if __name__ == '__main__':
    asyncio.run(main())
