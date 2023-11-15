from aiogram.fsm.state import StatesGroup, State

class Client(StatesGroup): # класс машины состояний для client хэндлера
    ptype = State()
    array = State()
    anon = State()

class Admin(StatesGroup): # класс машины состояний для admin хэндлера
    choose = State()