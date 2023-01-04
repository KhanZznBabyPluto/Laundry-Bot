from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import pymongo

import main

async def check_id(collection, id):
    obj = await collection.find({'id': id})
    if obj:
        return True
    return False

TOKEN_API = '5628547386:AAFJEdB3fWaZtpiejwUFCE9IijY6ZYJy4zM'

db_client = pymongo.MongoClient("mongodb+srv://andrey:28122011@cluster0.i2aesum.mongodb.net/?retryWrites=true&w=majority")
current_db = db_client['TeleBot']

collection = current_db['users']

storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot,
                storage=storage)


class ProfileStatesGroup(StatesGroup):

    name = State()
    surname = State()
    room_number = State()
    phone_number = State()


def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/authorize'))
    kb.add(KeyboardButton('/display_info'))
    kb.add(KeyboardButton('/order_laundry'))
    kb.add(KeyboardButton('/cancel'))

    return kb



@dp.message_handler(commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return

    await state.finish()
    await message.reply('Вы прервали запись!', reply_markup=get_kb())


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    await message.answer('Дорбро пожаловать! Чтобы привязать ваш аккаунт, введите - /authorize', reply_markup=get_kb())




@dp.message_handler(commands=['authorize'])
async def cmd_create(message: types.Message) -> None:
    #check if people are already connected
    global collection
    if check_id(collection, message.from_user.id):
        return await message.answer('Ваш телеграм аккаунт уже привязан')
    else:
        await message.reply("Давайте привяжем вас к вашему аккаунту. Введите ваше имя!")
    await ProfileStatesGroup.name.set() 



@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.name)
async def check_name(message: types.Message):
    await message.reply('Это не имя!')

@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['name'] = message.text

    await message.reply('Теперь отправь свою фамилию')
    await ProfileStatesGroup.next()



@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.surname)
async def check_surname(message: types.Message):
    await message.reply('Это не фамилия!')

@dp.message_handler(state=ProfileStatesGroup.surname)
async def load_surname(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['surname'] = message.text

    await message.reply('Введите номер комнаты')
    await ProfileStatesGroup.next()



@dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) > 1000 or float(message.text) < 100, state=ProfileStatesGroup.room_number)
async def check_room_number(message: types.Message):
    await message.reply('Введите реальный номер!')

@dp.message_handler(state=ProfileStatesGroup.room_number)
async def load_room_number(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['room_number'] = message.text

    await message.answer('Введите ваш номер телефона без различных знаков и пробелов')
    await ProfileStatesGroup.next()



@dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) < 87000000000 or float(message.text) > 88000000000, state=ProfileStatesGroup.phone_number)
async def check_phone_number(message: types.Message):
    await message.reply('Введите реальный номер!')

@dp.message_handler(state=ProfileStatesGroup.phone_number)
async def load_phone_number(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['phone_number'] = message.text

#   await check_people(state, user_id=message.from_user.id)
#   проверка полностью человека в БД по data
    global collection

    obj = collection.find_one_and_update({'surname': data['surname'], 'name': data['name'], 'room_num': int(data['room_number']), 'phone_num': str(data['phone_number'])}, {'$set': {'id': message.from_user.id}})

    if obj:
        await message.reply('А теперь перейдём к записи')
        await message.answer('Чтобы просмотреть свободные стиралки - введите /display_info. Чтобы выбрать время - /orderlaundry')
    else:
        await message.answer('Нет такого жителя!')
    await state.finish()
        
@dp.message_handler(commands=['display_info'])
async def display_handler(message: types.Message):
    res = main.available_time()
    print(res)
    await message.answer('Выберите время, чтобы посмотреть свободные стиральные машины:\n' + '\n'.join(res))




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)