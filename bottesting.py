from aiogram import types, executor, Bot, Dispatcher
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
# from aiogram.dispatcher.filters import Text
import keyboards as key
from keyboards import get_kb, get_ikb

from mongo import *
# import main

users_col = connect_collection("users")
book_col = connect_collection("book")

TOKEN_API = '5956900315:AAGUG4gCptqmSAtuWMO7zG-9itn_Wd8skNM'

storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)



class ProfileStatesGroup(StatesGroup):

    name = State()
    surname = State()
    room_number = State()
    phone_number = State()

Action = """
    Давайте перейдём к записи\nЧтобы просмотреть оставшееся количество стирок в этом месяце - нажмите <b>/Display_Info</b>\nЧтобы выбрать время - <b>/Order_Laundry</b>  """

Action_for_start = """
    Дорбро пожаловать!\nЧтобы привязать ваш аккаунт, нажмите - <b>/Authorize</b>\nЧтобы просмотреть оставшееся количество стирок в этом месяце - нажмите <b>/Display_Info</b>\nЧтобы выбрать время - <b>/Order_Laundry</b>"""

Action_for_stop = """
    Вас нет в списках проживающих. Бот остановлен.\nЕсли это ошибка в списках, то обратитесь к авторам Бота - @UnnwnKhanZz, @andrew0320\nЧтобы продолжить перезапустите бота полностью."""

@dp.message_handler(commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    if state is None:
        return

    await state.finish()
    await message.reply('Вы прервали запись!\nБот остановлен', reply_markup=get_kb())
    await dp.stop_polling()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    await message.answer(text = Action_for_start, parse_mode='HTML', reply_markup=get_kb())



@dp.message_handler(commands=['authorize'])
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
async def load_name(message: types.Message, state: FSMContext) -> None:
    if not check_key(users_col, "name", message.text):
        await message.answer(text = Action_for_stop)
        await dp.stop_polling()

    async with state.proxy() as data:
        data['name'] = message.text

    await message.answer('Теперь отправьте свою фамилию')
    await ProfileStatesGroup.next()



@dp.message_handler(lambda message: not message.text or message.text.isdigit(), state=ProfileStatesGroup.surname)
async def check_surname(message: types.Message):
    await message.reply('Это не фамилия!')

@dp.message_handler(state=ProfileStatesGroup.surname)
async def load_surname(message: types.Message, state: FSMContext) -> None:
    if not check_key(users_col, "surname", message.text):
        await message.answer(text = Action_for_stop)
        await dp.bot.stop(message.from_user.id)
        

    async with state.proxy() as data:
        data['surname'] = message.text

    await message.answer('Введите номер комнаты')
    await ProfileStatesGroup.next()


# @dp.message_handler(lambda message: not message.text or message.text.isdigit(), state=ProfileStatesGroup.surname)
# async def check_surname(message: types.Message, state: FSMContext):
#     if not message.text.isalpha():
#         await message.reply('Это не фамилия!')
#         return
#     async with state.proxy() as data:
#         data['surname'] = message.text

# # Define the load_surname handler
# @dp.message_handler(state=ProfileStatesGroup.room_number)
# async def load_surname(message: types.Message, state: FSMContext):
#     # Check if the user is in the list of residents
#     if not check_key(users_col, "surname", message.text):
#         await message.answer('Вас нет в списках проживающих. Бот остановлен.\nЕсли это ошибка в списках, то обратитесь к авторам Бота')
#         await dp.stop_polling()
#         return

#     # Save the room number in the state
#     async with state.proxy() as data:
#         data['room_number'] = message.text

#     # End the conversation flow
#     await ProfileStatesGroup.next()



@dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) > 1000 or float(message.text) < 100, state=ProfileStatesGroup.room_number)
async def check_room_number(message: types.Message):
    await message.reply('Введите реальный номер!')

@dp.message_handler(state=ProfileStatesGroup.room_number)
async def load_room_number(message: types.Message, state: FSMContext) -> None:
    if not check_key(users_col, "room_num", message.text):
        await message.answer(text = Action_for_stop)
        await dp.stop_polling()

    async with state.proxy() as data:
        data['room_number'] = message.text

    await message.answer('Введите ваш номер телефона без различных знаков и пробелов')
    await ProfileStatesGroup.next()



@dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) < 87000000000 or float(message.text) > 88000000000, state=ProfileStatesGroup.phone_number)
async def check_phone_number(message: types.Message):
    await message.reply('Введите реальный номер!')

@dp.message_handler(state=ProfileStatesGroup.phone_number)
async def load_phone_number(message: types.Message, state: FSMContext) -> None:
    if not check_key(users_col, "phone_num", message.text):
        await message.answer(text = Action_for_stop)
        await dp.stop_polling()

    async with state.proxy() as data:
        data['phone_number'] = message.text

    filter = {"phone_num" : message.text}
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
    await callback.message.answer(text='Вы зарегистрировались на промежуток 9 - 10')
    
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    # change_key_book(book_col, {"time" : {"9.00-10.00" : True}}, "9.00-10.00", False)
    flag = 0
    for j in range(7):
        if flag:
            await callback.answer('Извините, все машинки  на это время заняты!')
            break
        if key.collection[0][j]:
            key.collection[0][j] = False
            flag = 1                
            await callback.answer(f'Номер вашей машинки - {j+1}')
    await callback.answer()


@dp.callback_query_handler(text = "tentoeleven")
async def ten_to_el_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 10 - 11')
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    # change_key_book(book_col, {"time" : {"10.00-11.00" : True}}, "10.00-11.00", False)
    flag = 0
    for j in range(7):
        if flag:
            await callback.answer('Извините, все машинки  на это время заняты!')
            break
        if key.collection[1][j]:
            key.collection[1][j] = False
            flag = 1                
            await callback.answer(f'Номер вашей машинки - {j+1}')
    await callback.answer()


@dp.callback_query_handler(text = "eleventotwelve")
async def el_to_twelve_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 11 - 12')
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    flag = 0
    for j in range(7):
        if flag:
            await callback.answer('Извините, все машинки  на это время заняты!')
            break
        if key.collection[2][j]:
            key.collection[2][j] = False
            flag = 1                
            await callback.answer(f'Номер вашей машинки - {j+1}')
    await callback.answer()


@dp.callback_query_handler(text = "twelvetothirteen")
async def twelve_to_thir_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 12 - 13')
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    flag = 0
    for j in range(7):
        if flag:
            await callback.answer('Извините, все машинки  на это время заняты!')
            break
        if key.collection[3][j]:
            key.collection[3][j] = False
            flag = 1                
            await callback.answer(f'Номер вашей машинки - {j+1}')
    await callback.answer()


@dp.callback_query_handler(text = "thirteentofourteen")
async def thir_to_four_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 13 - 14')
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    flag = 0
    for j in range(7):
        if flag:
            await callback.answer('Извините, все машинки  на это время заняты!')
            break
        if key.collection[4][j]:
            key.collection[4][j] = False
            flag = 1                
            await callback.answer(f'Номер вашей машинки - {j+1}')
    await callback.answer()


@dp.callback_query_handler(text = "fourteentofifteen")
async def four_to_fif_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 14 - 15')
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    flag = 0
    for j in range(7):
        if flag:
            await callback.answer('Извините, все машинки  на это время заняты!')
            break
        if key.collection[5][j]:
            key.collection[5][j] = False
            flag = 1                
            await callback.answer(f'Номер вашей машинки - {j+1}')
    await callback.answer()


@dp.callback_query_handler(text = "fifteentosixteen")
async def fif_to_six_handler(callback: types.CallbackQuery):
    await callback.message.answer(text='Вы зарегистрировались на промежуток 15 - 16')
    user = give_user(users_col, callback.from_user.id)
    state_of_orders = int(user["orderes"]) - 1
    change_key(users_col, {"id" : callback.from_user.id}, "orderes", state_of_orders)
    flag = 0
    for j in range(7):
        if flag:
            await callback.answer('Извините, все машинки  на это время заняты!')
            break
        if key.collection[6][j]:
            key.collection[6][j] = False
            flag = 1                
            await callback.answer(f'Номер вашей машинки - {j+1}')
    await callback.answer()




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)