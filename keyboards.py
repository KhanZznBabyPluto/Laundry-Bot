from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
import mongo

def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/Authorize'))
    kb.add(KeyboardButton('/Display_info'))
    kb.add(KeyboardButton('/Order_laundry'))
    kb.add(KeyboardButton('/Cancel'))

    
    return kb

collection = [[True for i in range(7)] for j in range(7)]




collecton_ikb = [
                InlineKeyboardButton(text='с 9:00 до 10:10', callback_data='ninetoten'), 
                InlineKeyboardButton(text='с 10:10 до 11:20', callback_data='tentoeleven'),
                InlineKeyboardButton(text='с 11:20 до 12:30', callback_data='eleventotwelve'),
                InlineKeyboardButton(text='с 12:30 до 13:40', callback_data='twelvetothirteen'),
                InlineKeyboardButton(text='с 13:40 до 14:50', callback_data='thirteentofourteen'),
                InlineKeyboardButton(text='с 14:50 до 16:00', callback_data='fourteentofifteen'),
                InlineKeyboardButton(text='с 16:00 до 17:00', callback_data='fifteentosixteen')
]

empty_markup = InlineKeyboardMarkup()


reactivate_kb = ReplyKeyboardMarkup(resize_keyboard=True)
reactivate_kb.add(KeyboardButton('/Reactivate_bot'))



def get_ikb() -> InlineKeyboardMarkup:
    global collection
    global collecton_ikb

    ikb = InlineKeyboardMarkup(row_width=2)

    available = []
    available = mongo.available_time_bool()

    for i in range(0, 7):
        if available[i] == True:
            ikb1 = collecton_ikb[i]
            ikb.add(ikb1)
        else:
            continue

    return ikb