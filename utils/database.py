import asyncpg

class DataBase:
    def __init__(self): # данные для входа в базу
        self.user = 'user_bot'
        self.password = '123456'
        self.database = 'bot_db'
        self.host = 'localhost'
        self.port = 5432

    async def connect(self): # функция подключения к базе
        self.conn = await asyncpg.connect(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
            port=self.port
        )

    async def disconnect(self): # функция разрыва соединения с базой (изменения применяются автоматически)
        if self.conn:
            await self.conn.close()

    async def create_table(self): # создание таблицы для работы бота
        await self.connect()
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                username TEXT DEFAULT 'аноним',
                media TEXT,
                description TEXT NOT NULL,
                status VARCHAR(25) DEFAULT 'Обработка',
                type VARCHAR(25) NOT NULL,
                video BOOLEAN NOT NULL DEFAULT FALSE
            )
        ''')
        await self.disconnect()

    """СОЗДАНИЕ ТИКЕТОВ"""

    async def create_ticket_media(self, data, query): # создание поста с медиа-файлом
        await self.connect()
        await self.conn.execute('INSERT INTO tickets (user_id, username, media, description, type, video) VALUES ($1,$2,$3,$4,$5,$6)', data['userid'], query.from_user.username, data['media'], data['description'], data['post_type'], data['video']) # запись полученных данных с машины состояний в БД
        await self.disconnect()

    async def create_ticket(self, data, query): # создание поста без медиа-файла
        await self.connect()
        await self.conn.execute('INSERT INTO tickets (user_id, username, description, type) VALUES ($1,$2,$3,$4)', data['userid'], query.from_user.username, data['description'], data['post_type']) # запись полученных данных с машины состояний в БД
        await self.disconnect()

    async def create_anon_media(self, data): # создание АНОНИМНОГО поста с медиа-файлом 
        await self.connect()
        await self.conn.execute('INSERT INTO tickets (user_id, media, description, type, video) VALUES ($1,$2,$3,$4,$5)', data['userid'], data['media'], data['description'], data['post_type'], data['video']) # запись полученных данных с машины состояний в БД
        await self.disconnect()

    async def create_anon(self, data): # создание АНОНИМНОГО поста без медиа-файла
        await self.connect()
        await self.conn.execute('INSERT INTO tickets (user_id, description, type) VALUES ($1,$2,$3)', data['userid'], data['description'], data['post_type']) # запись полученных данных с машины состояний в БД
        await self.disconnect()

    """ПОЛУЧЕНИЕ СПИСКА ТИКЕТОВ"""

    async def get_tickets(self, message, status):
        if status == 'pending': # проверка статуса объявлений, получаемого из функции get_pending(). Смотреть в admin_handler
            result = '' # создание пустой переменной необходимо, чтобы избмежать ошибку, если данных не будет
            await self.connect()
            rows = await self.conn.fetch('SELECT * FROM tickets WHERE status = $1', 'Обработка') # получаем массив со словарями 
            for row in rows: # перебираем массив, создавая готовый список постов
                result += f"<b>Объявление: <code>{row['ticket_id']}</code></b>\nОтправитель: @{row['username']}\n\n"
            await self.disconnect()
            return result # возвращаем готовый список постов
        
        # получение списка ВСЕХ постов в базе
        result = '' 
        await self.connect()
        rows = await self.conn.fetch('SELECT * FROM tickets')
        for row in rows:
            result += f"Объявление: <code>{row['ticket_id']}</code>\nСтатус: <i><b>{row['status']}</b></i>\nОтправитель: @{row['username']}\n\n"
        await self.disconnect()
        return result # если данных накопилось слишком много, данная команда может перестать работать корректно
    
    """РАБОТА С ВЫБРАННЫМ ТИКЕТОМ"""

    async def get_ticket(self, ticketID): # аргумент ticketID передается из функции select(). Смотреть в admin_handler
        result = None
        await self.connect()
        result = await self.conn.fetch('SELECT * FROM tickets WHERE ticket_id = $1', ticketID) # выбор поста из БД по его ticket_id
        result = result[0] # используется для выбора первого словаря в полученном массиве
        await self.disconnect()
        return result # возвращение словаря
    

    async def edit_ticket(self, ticketID): # функция изменения статуса поста
        await self.connect()
        await self.conn.execute('UPDATE tickets SET status = $1 WHERE ticket_id = $2', 'Опубликован', ticketID) # изменяем статус поста по его ticket_id
        await self.disconnect()

    
    async def remove_ticket(self, ticketID): # функция удаления поста
        await self.connect()
        await self.conn.execute('DELETE FROM tickets WHERE ticket_id = $1', ticketID) # удаляем пост из БД по его ticket_id
        await self.disconnect()
