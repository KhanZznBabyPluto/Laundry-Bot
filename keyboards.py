from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text

def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/Authorize'))
    kb.add(KeyboardButton('/Display_Info'))
    kb.add(KeyboardButton('/Order_Laundry'))
    kb.add(KeyboardButton('/Cancel'))

    
    return kb

collection = [True, True, True, True, True, True, True, True]

collecton_ikb = [
                InlineKeyboardButton(text='с 9 до 10', callback_data='ninetoten'), 
                InlineKeyboardButton(text='с 10 до 11', callback_data='tentoeleven'),
                InlineKeyboardButton(text='с 11 до 12', callback_data='eleventotwelve'),
                InlineKeyboardButton(text='с 12 до 13', callback_data='twelvetothirteen'),
                InlineKeyboardButton(text='с 13 до 14', callback_data='thirteentofourteen'),
                InlineKeyboardButton(text='с 14 до 15', callback_data='fourteentofifteen'),
                InlineKeyboardButton(text='с 15 до 16', callback_data='fifteentosixteen'),
                InlineKeyboardButton(text='с 16 до 17', callback_data='sixteentoseventeen')
]




def get_ikb() -> InlineKeyboardMarkup:
    global collection
    global collecton_ikb

    ikb = InlineKeyboardMarkup(row_width=2)

    for i in range(0, 8):
        if collection[i]:
            ikb1 = collecton_ikb[i]
            ikb.add(ikb1)
        else:
            continue

    return ikb