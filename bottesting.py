from aiogram import types, executor, Bot, Dispatcher
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
# from aiogram.dispatcher.filters import Text
import keyboards as key
from keyboards import get_kb, get_ikb, reactivate_kb, recieve_document_kb

from mongo import *


users_col = connect_collection("users")
book_col = connect_collection("book")


TOKEN_API = '5956900315:AAGUG4gCptqmSAtuWMO7zG-9itn_Wd8skNM'

storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)

class UserStates(StatesGroup):
    ACTIVE = State()
    INACTIVE = State() 

class ProfileStatesGroup(StatesGroup):
    name = State()
    surname = State()
    phone_number = State()
    room_number = State()
    password = State()


Action = """
    Давайте перейдём к записи\nЧтобы просмотреть оставшееся количество стирок в этом месяце - нажмите <b>/Display_Info</b>\nЧтобы выбрать время - <b>/Order_Laundry</b>"""

Action_for_start = """
    Дорбро пожаловать!\nЧтобы привязать ваш аккаунт, нажмите - <b>/Authorize</b>\nЧтобы просмотреть оставшееся количество стирок в этом месяце - нажмите <b>/Display_Info</b>\nЧтобы выбрать время - <b>/Order_Laundry</b>"""

Action_for_stop = """
    Бот остановлен. Вас нет в списках проживающих или вы неправильно ввели данные.\nПопробуйте ввести данные снова.\nЕсли это ошибка в списках, то обратитесь к авторам Бота - @UnnwnKhanZz, @andrew0320"""


@dp.message_handler(commands=['Cancel'])
async def cmd_cancel(message: types.Message):
    await message.reply('Вы прервали запись!\nБот приостановлен, для перезапуска нажмите кнопку ниже ↓', reply_markup= reactivate_kb)
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
    if check_key(users_col, "id", message.from_user.id):
        await message.answer("Вы уже подключены, авторизовываться не надо")
        await message.answer(text = Action, parse_mode='HTML')
    else:
        await message.answer("Давайте привяжем вас к вашему аккаунту. Введите ваше имя")
        await ProfileStatesGroup.name.set() 


@dp.message_handler(lambda message: not message.text, state=ProfileStatesGroup.name)
async def check_name(message: types.Message):
    await message.reply('Это не имя!')

@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.name)
async def load_name(message: types.Message) -> None:
    if not check_key(users_col, "name", message.text):
        await message.answer(text = Action_for_stop)
        await dp.bot.stop(message.from_user.id)

    if message == 'admin':
        await message.answer('Введите пароль')
        await ProfileStatesGroup.password()
    else:
        await message.answer('Теперь отправьте свою фамилию')
        await ProfileStatesGroup.next()


@dp.message_handler(state = ProfileStatesGroup.password)
async def admin_keyboard(message: types.Message) -> None:
    if message == '12345':
        await message.answer('Для получения списка записей на сегодня, нажмите кнопку ниже ↓', reply_markup=recieve_document_kb)
    else:
        await message.asnwer('Пароль введён неверно!\nБот приостановлен')
        dp.bot.stop(message.from_user.id)

@dp.message_handler(commands = ['Receive_Document'])
async def document_push(message: types.Message):
    await message.answer('d;dwa') # здесь выгрузка документа


@dp.message_handler(lambda message: not message.text or message.text.isdigit(), state=ProfileStatesGroup.surname)
async def check_surname(message: types.Message):
    await message.reply('Это не фамилия!')

@dp.message_handler(state=ProfileStatesGroup.surname)
async def load_surname(message: types.Message) -> None:
    if not check_key(users_col, "surname", message.text):
        await message.answer(text = Action_for_stop)
        await dp.bot.stop(message.from_user.id)

    await message.answer('Введите ваш номер телефона без различных знаков и пробелов')
    await ProfileStatesGroup.next()


@dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) < 87000000000 or float(message.text) > 90000000000, state=ProfileStatesGroup.phone_number)
async def check_phone_number(message: types.Message):
    await message.reply('Введите реальный номер!')

@dp.message_handler(state=ProfileStatesGroup.phone_number)
async def load_phone_number(message: types.Message) -> None:
    if not check_key(users_col, "phone_num", message.text):
        await message.answer(text = Action_for_stop)
        await dp.bot.stop(message.from_user.id)

    await message.answer('Введите номер комнаты')
    await ProfileStatesGroup.next()


@dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) > 1000 or float(message.text) < 100, state=ProfileStatesGroup.room_number)
async def check_room_number(message: types.Message):
    await message.reply('Введите реальный номер!')

@dp.message_handler(state=ProfileStatesGroup.room_number)
async def load_room_number(message: types.Message,  state: FSMContext) -> None:
    if not check_key(users_col, "room_num", message.text):
        await message.answer(text = Action_for_stop)
        await dp.bot.stop(message.from_user.id)

    filter = {"room_num" : message.text}
    change_key(users_col, filter, "id", message.from_user.id)

    await message.answer(text = Action, parse_mode='HTML')
    await state.finish()


@dp.message_handler(commands=['Display_Info'])
async def display_handler(message: types.Message):
    user = give_user(users_col, message.from_user.id)
    await message.answer(f'Оставшееся количество стирок: {user["orderes"]}\n')   


@dp.message_handler(commands=['Order_Laundry'])
async def orderlaundry(message: types.Message):
    user = give_user(users_col, message.from_user.id)
    if user["orderes"] <= 0:
        await message.answer('У вас закончились свободные стирки')
    else:
        await bot.send_message(chat_id = message.from_user.id, text='Выберите свободный промежуток для записи', reply_markup=get_ikb())


@dp.callback_query_handler(text = "ninetoten")
async def nine_to_ten_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text='Вы зарегистрировались на промежуток 9:00 - 10:10')
    
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)

    washing_id = change_key_book(book_col, "9.00-10.00", False)
    await callback.message.answer(text = f'Номер вашей машинки - {washing_id}')

    await callback.answer()


@dp.callback_query_handler(text = "tentoeleven")
async def ten_to_el_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text='Вы зарегистрировались на промежуток 10:10 - 11:20')
    
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    
    washing_id = change_key_book(book_col, "10.00-11.00", False)
    await callback.message.answer(text = f'Номер вашей машинки - {washing_id}')

    await callback.answer()


@dp.callback_query_handler(text = "eleventotwelve")
async def el_to_twelve_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text='Вы зарегистрировались на промежуток 11:20 - 12:30')
    
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    
    washing_id = change_key_book(book_col, "11.00-12.00", False)
    await callback.message.answer(text = f'Номер вашей машинки - {washing_id}')
    
    await callback.answer()


@dp.callback_query_handler(text = "twelvetothirteen")
async def twelve_to_thir_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text='Вы зарегистрировались на промежуток 12:30 - 13:40')
    
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    
    washing_id = change_key_book(book_col, "12.00-13.00", False)
    await callback.message.answer(text = f'Номер вашей машинки - {washing_id}')
    
    await callback.answer()


@dp.callback_query_handler(text = "thirteentofourteen")
async def thir_to_four_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text='Вы зарегистрировались на промежуток 13:40 - 14:50')
    
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    
    washing_id = change_key_book(book_col, "13.00-14.00", False)
    await callback.message.answer(text = f'Номер вашей машинки - {washing_id}')
    
    await callback.answer()


@dp.callback_query_handler(text = "fourteentofifteen")
async def four_to_fif_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text='Вы зарегистрировались на промежуток 14:50 - 16:00')

    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    
    washing_id = change_key_book(book_col, "14.00-15.00", False)
    await callback.message.answer(text = f'Номер вашей машинки - {washing_id}')

    await callback.answer()


@dp.callback_query_handler(text = "fifteentosixteen")
async def fif_to_six_handler(callback: types.CallbackQuery):
    await bot.edit_message_reply_markup(chat_id = callback.message.chat.id, message_id = callback.message.message_id, reply_markup = None)
    await callback.message.answer(text='Вы зарегистрировались на промежуток 16:00 - 17:00')
    
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    
    washing_id = change_key_book(book_col, "15.00-16.00", False)
    await callback.message.answer(text = f'Номер вашей машинки - {washing_id}')

    await callback.answer()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)