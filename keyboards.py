from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text

def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/Authorize'))
    kb.add(KeyboardButton('/Display_info'))
    kb.add(KeyboardButton('/Order_laundry'))
    kb.add(KeyboardButton('/Cancel'))

    
    return kb

collection = [[True for i in range(7)] for j in range(7)]

collecton_ikb = [
                InlineKeyboardButton(text='с 9 до 10:10', callback_data='ninetoten'), 
                InlineKeyboardButton(text='с 10:10 до 11:20', callback_data='tentoeleven'),
                InlineKeyboardButton(text='с 11:20 до 12:30', callback_data='eleventotwelve'),
                InlineKeyboardButton(text='с 12:30 до 13:40', callback_data='twelvetothirteen'),
                InlineKeyboardButton(text='с 13:40 до 14:50', callback_data='thirteentofourteen'),
                InlineKeyboardButton(text='с 14:50 до 16', callback_data='fourteentofifteen'),
                InlineKeyboardButton(text='с 16 до 17', callback_data='fifteentosixteen')
]




def get_ikb(a = 0, b = 6) -> InlineKeyboardMarkup:
    global collection
    global collecton_ikb

    ikb = InlineKeyboardMarkup(row_width=2)

    for i in range(a, b+1):
        if collection[i]:
            ikb1 = collecton_ikb[i]
            ikb.add(ikb1)
        else:
            continue

    return ikb