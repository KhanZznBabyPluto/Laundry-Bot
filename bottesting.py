from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
# from aiogram.dispatcher.filters import Text
import keyboards as key
from keyboards import get_kb, get_ikb

import mongo
# import pymongo
# import main

TOKEN_API = '5628547386:AAFJEdB3fWaZtpiejwUFCE9IijY6ZYJy4zM'

state_of_ordered = 4

storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)

# db_client = pymongo.MongoClient("mongodb+srv://KhanZz:<password>@digitalqueue.ojmlals.mongodb.net/?retryWrites=true&w=majority")
# current_db = db_client['digital_queue']
# collection_db = current_db['users']



class ProfileStatesGroup(StatesGroup):

    name = State()
    surname = State()
    room_number = State()
    phone_number = State()

Action = """
    А теперь перейдём к записи\nЧтобы просмотреть оставшееся количество стирок в этом месяце - нажмите <b>/Display_Info</b>\nЧтобы выбрать время - <b>/Order_Laundry</b>  """




@dp.message_handler(commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return

    await state.finish()
    await message.reply('Вы прервали запись!', reply_markup=get_kb())


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    await message.answer('Дорбро пожаловать! Чтобы привязать ваш аккаунт, нажмите - /authorize', reply_markup=get_kb())



@dp.message_handler(commands=['authorize'])
async def cmd_create(message: types.Message) -> None:
    #check if people are already connected
    await message.answer("Давайте привяжем вас к вашему аккаунту. Введите ваше имя")
    await ProfileStatesGroup.name.set() 



@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.name)
async def check_name(message: types.Message):
    await message.reply('Это не имя!')

@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['name'] = message.text

    await message.answer('Теперь отправьте свою фамилию')
    await ProfileStatesGroup.next()



@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.surname)
async def check_surname(message: types.Message):
    await message.reply('Это не фамилия!')

@dp.message_handler(state=ProfileStatesGroup.surname)
async def load_surname(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['surname'] = message.text

    await message.answer('Введите номер комнаты')
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

    await message.answer(text = Action, parse_mode='HTML')
    await state.finish()

@dp.message_handler(commands=['Display_Info'])
async def display_handler(message: types.Message):
    global state_of_ordered
    await message.answer(f'Оставшееся количество стирок: {state_of_ordered}\n')   



@dp.message_handler(commands=['Order_Laundry'])
async def orderlaundry(message: types.Message):
    global state_of_ordered
    if state_of_ordered == 0:
        await message.answer('У вас закончились свободные стирки')
    else:
        await bot.send_message(chat_id = message.from_user.id, text='Выберите свободный промежуток для записи', reply_markup=get_ikb())


@dp.callback_query_handler(text = "ninetoten")
async def nine_to_ten_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 9 - 10')
    # global collection, state_of_ordered
    global state_of_ordered
    key.collection[0] = False
    state_of_ordered -= 1
    await callback.answer()


@dp.callback_query_handler(text = "tentoeleven")
async def ten_to_el_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 10 - 11')
    # global collection, state_of_ordered
    global state_of_ordered
    key.collection[1] = False
    state_of_ordered -= 1
    await callback.answer()


@dp.callback_query_handler(text = "eleventotwelve")
async def el_to_twelve_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 11 - 12')
    # global collection, state_of_ordered
    global state_of_ordered
    key.collection[2] = False
    state_of_ordered -= 1
    await callback.answer()


@dp.callback_query_handler(text = "twelvetothirteen")
async def twelve_to_thir_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 12 - 13')
    # global collection, state_of_ordered
    global state_of_ordered
    key.collection[3] = False
    state_of_ordered -= 1
    await callback.answer()


@dp.callback_query_handler(text = "thirteentofourteen")
async def thir_to_four_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 13 - 14')
    # global collection, state_of_ordered
    global state_of_ordered
    key.collection[4] = False
    state_of_ordered -= 1
    await callback.answer()

@dp.callback_query_handler(text = "fourteentofifteen")
async def four_to_fif_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 13 - 14')
    # global collection, state_of_ordered
    global state_of_ordered
    key.collection[5] = False
    state_of_ordered -= 1
    await callback.answer()

@dp.callback_query_handler(text = "fifteentosixteen")
async def fif_to_six_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 13 - 14')
    # global collection, state_of_ordered
    global state_of_ordered
    key.collection[6] = False
    state_of_ordered -= 1
    await callback.answer()

@dp.callback_query_handler(text = "sixteentoseventeen")
async def six_to_sev_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 13 - 14')
    # global collection, state_of_ordered
    global state_of_ordered
    key.collection[7] = False
    state_of_ordered -= 1
    await callback.answer()




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)