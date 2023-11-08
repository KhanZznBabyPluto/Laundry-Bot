from aiogram import types, executor, Bot, Dispatcher
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
import keyboards as key
from keyboards import get_kb, get_ikb, reactivate_kb, recieve_document_kb, times

from class_user import User
from mongo import *


users_col = connect_collection("users")
book_col = connect_collection("book")
user = User()

TOKEN_API = '5956900315:AAGUG4gCptqmSAtuWMO7zG-9itn_Wd8skNM'
# TOKEN_API_NEW = '6505220403:AAFqKWRmlSUqHlvMr7WTTVjZGLjj6GNFuOw'

storage = MemoryStorage()
# PROXY_URL = "http://proxy.server:3128"
# bot = Bot(token=TOKEN_API, proxy=PROXY_URL)
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)


class UserStates(StatesGroup):
    ACTIVE = State()
    INACTIVE = State() 

class ProfileStatesGroup(StatesGroup):
    name = State()
    surname = State()
    room_number = State()
    phone_number = State()
    password = State()


Action = """
    Давайте перейдём к записи\nЧтобы просмотреть оставшееся количество стирок в этом месяце - нажмите <b>/Display_Info</b>\nЧтобы выбрать время - <b>/Order_Laundry</b>"""

Action_for_start = """
    Дорбро пожаловать!\nЧтобы привязать ваш аккаунт, нажмите - <b>/Authorize</b>\nЧтобы просмотреть оставшееся количество стирок в этом месяце - нажмите <b>/Display_Info</b>\nЧтобы выбрать время - <b>/Order_Laundry</b>"""

Action_for_stop = """
    Бот остановлен. Вас нет в списках проживающих или вы неправильно ввели данные.\nПопробуйте ввести данные снова.\nЕсли это ошибка в списках, то обратитесь к авторам Бота - @Khangeldin_Ansar, @andrew0320"""

Action_for_non_auth = """
    Вы не авторизованы, поэтому я не могу показать вам информацию по оставшимся стиркам.\nПожалуйста авторизуйтесь - <b>/Authorize</b> или остановите бота - <b>/Cancel</b>"""

Action_for_reset = """
    Вы прервали запись!\nБот приостановлен, для перезапуска нажмите кнопку ниже ↓"""


@dp.message_handler(commands=['Cancel'])
async def cmd_cancel(message: types.Message):
    await message.reply(text=Action_for_reset, parse_mode='HTML', reply_markup= reactivate_kb)
    await UserStates.INACTIVE.set()


@dp.message_handler(commands=['Reactivate_bot'], state=UserStates.INACTIVE)
async def reactivate_bot(message: types.Message):
    await message.answer('Бот перезапущен')
    await message.answer(text= Action_for_start, parse_mode = 'HTML', reply_markup=get_kb())
    await UserStates.ACTIVE.set()


@dp.message_handler(commands=['Start'])
async def cmd_start(message: types.Message) -> None:
    await message.answer(text = Action_for_start, parse_mode='HTML', reply_markup=get_kb())


@dp.message_handler(commands=['Authorize'])
async def cmd_create(message: types.Message) -> None:
    global user
    user = User()
    if check_key(["id"], [message.from_user.id]):
        await message.answer("Вы уже подключены, авторизовываться не надо")
        user.update_name(give_name_by_id(message.from_user.id), message.from_user.id)
        await message.answer(text = Action, parse_mode='HTML')
    else:
        await message.answer("Давайте привяжем вас к вашему аккаунту. Введите ваше имя")
        await ProfileStatesGroup.name.set() 


@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.name)
async def check_name(message: types.Message):
    await message.reply('Это не имя!')

@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.name)
async def load_name(message: types.Message) -> None:
    global user
    if not check_key(["name"], [message.text]):
        await message.answer(text = Action_for_stop)
        await dp.bot.stop_poll(chat_id=message.from_user.id, message_id=message.message_id)
        await UserStates.INACTIVE.set()

    if message == 'admin':
        await message.answer('Введите пароль')
        await ProfileStatesGroup.password()
    else:
        user.update_name(message.text, message.from_user.id)
        await message.answer('Теперь отправьте свою фамилию')
        await ProfileStatesGroup.next()


@dp.message_handler(state = ProfileStatesGroup.password)
async def admin_keyboard(message: types.Message) -> None:
    if message == '12345':
        await message.answer('Для получения списка записей на сегодня, нажмите кнопку ниже ↓', reply_markup=recieve_document_kb)
    else:
        await message.asnwer('Пароль введён неверно!\nБот приостановлен')
        await dp.bot.stop_poll(chat_id=message.from_user.id, message_id=message.message_id)

@dp.message_handler(commands = ['Receive_Document'])
async def document_push(message: types.Message):
    await message.answer('d;dwa') # здесь выгрузка документа


@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.surname)
async def check_surname(message: types.Message):
    await message.reply('Это не фамилия!')

@dp.message_handler(state=ProfileStatesGroup.surname)
async def load_surname(message: types.Message) -> None:
    global user
    if not check_key(["name", "surname"], [user.name, message.text]):
        await message.answer(text = Action_for_stop)
        await dp.bot.stop_poll(chat_id=message.from_user.id, message_id=message.message_id)
        await UserStates.INACTIVE.set()

    user.update_surname(message.text)
    await message.answer('Введите номер вашей комнаты')
    await ProfileStatesGroup.next()


@dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) > 1000 or float(message.text) < 100, state=ProfileStatesGroup.room_number)
async def check_room_number(message: types.Message):
    await message.reply('Введите реальный номер!')

@dp.message_handler(state=ProfileStatesGroup.room_number)
async def load_room_number(message: types.Message) -> None:
    global user
    user.update_room_number(message.text)
    if not check_key(["name", "surname", "room"], [user.name, user.surname, user.room]):
        await message.answer(text = Action_for_stop)
        await dp.bot.stop_poll(chat_id=message.from_user.id, message_id=message.message_id)
        await UserStates.INACTIVE.set()

    await message.answer('Введите ваш номер телефона без различных пробелов и знаков')
    await ProfileStatesGroup.next()


@dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) < 87000000000 or float(message.text) > 90000000000, state=ProfileStatesGroup.phone_number)
async def check_phone_number(message: types.Message):
    await message.reply('Введите реальный номер!')

@dp.message_handler(state=ProfileStatesGroup.phone_number)
async def load_phone_number(message: types.Message, state: FSMContext) -> None:
    global user
    add_info(user.name, user.surname, user.room, message.text, user.id)
    
    # 
    await message.answer(text = Action, parse_mode='HTML')
    await state.finish()



# @dp.message_handler(commands=['Display_Info'])
# async def display_handler(message: types.Message):
#     if user.flag:
#         await message.answer(f'Оставшееся количество стирок: {give_user_number_orders(message.from_user.id)}\n')   
#     else:
#         await message.answer(text=Action_for_non_auth, parse_mode='HTML')

@dp.message_handler(commands=['Display_Info'])
async def display_handler(message: types.Message):
    await message.answer(f'Оставшееся количество стирок: {give_user_number_orders(message.from_user.id)}\n')   

@dp.message_handler(commands=['Order_Laundry'])
async def orderlaundry(message: types.Message):
    if give_user_number_orders(message.from_user.id) <= 0:
        await message.answer('У вас закончились свободные стирки')
        await UserStates.INACTIVE.set()
    else:
        await bot.send_message(chat_id = message.from_user.id, text='Выберите свободный промежуток для записи', reply_markup=get_ikb())




@dp.callback_query_handler(text='0')
async def nine_to_ten_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text=f'Вы зарегистрировались на промежуток {times[0]}')
    
    global user
    user.orders = give_user_number_orders(callback.from_user.id)
    user.orders -= 1
    change_number_orders(callback.from_user.id, user.orders)

    washer_id = change_free_time_by_first(times[0], False)
    await callback.message.answer(text = f'Номер вашей машинки - {washer_id}')


    await callback.answer()


@dp.callback_query_handler(text='1')
async def ten_to_el_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text=f'Вы зарегистрировались на промежуток {times[1]}')
    
    global user
    user.orders = give_user_number_orders(callback.from_user.id)
    user.orders -= 1
    change_number_orders(callback.from_user.id, user.orders)
    
    washer_id = change_free_time_by_first(times[1], False)
    await callback.message.answer(text = f'Номер вашей машинки - {washer_id}')

    await callback.answer()


@dp.callback_query_handler(text='2')
async def el_to_twelve_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text=f'Вы зарегистрировались на промежуток {times[2]}')
    
    global user
    user.orders = give_user_number_orders(callback.from_user.id)
    user.orders -= 1
    change_number_orders(callback.from_user.id, user.orders)
    
    washer_id = change_free_time_by_first(times[2], False)
    await callback.message.answer(text = f'Номер вашей машинки - {washer_id}')
    
    await callback.answer()


@dp.callback_query_handler(text='3')
async def twelve_to_thir_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text=f'Вы зарегистрировались на промежуток {times[3]}')
    
    global user
    user.orders = give_user_number_orders(callback.from_user.id)
    user.orders -= 1
    change_number_orders(callback.from_user.id, user.orders)
    
    washer_id = change_free_time_by_first(times[3], False)
    await callback.message.answer(text = f'Номер вашей машинки - {washer_id}')
    
    await callback.answer()


@dp.callback_query_handler(text='4')
async def thir_to_four_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text=f'Вы зарегистрировались на промежуток {times[4]}')
    
    global user
    user.orders = give_user_number_orders(callback.from_user.id)
    user.orders -= 1
    change_number_orders(callback.from_user.id, user.orders)
    
    washer_id = change_free_time_by_first(times[4], False)
    await callback.message.answer(text = f'Номер вашей машинки - {washer_id}')
    
    await callback.answer()


@dp.callback_query_handler(text='5')
async def four_to_fif_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text=f'Вы зарегистрировались на промежуток {times[5]}')

    global user
    user.orders = give_user_number_orders(callback.from_user.id)
    user.orders -= 1
    change_number_orders(callback.from_user.id, user.orders)
    
    washer_id = change_free_time_by_first(times[5], False)
    await callback.message.answer(text = f'Номер вашей машинки - {washer_id}')

    await callback.answer()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)