from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
from mongo import *

times = ['9.00-10.10', '10.10-11.20', '11.20-12.30', '12.30-14.00', '14.00-15.10', '15.10-16.20']

def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/Authorize'))
    kb.add(KeyboardButton('/Display_info'))
    kb.add(KeyboardButton('/Order_laundry'))
    kb.add(KeyboardButton('/Cancel'))

    
    return kb

collecton_ikb = [
                InlineKeyboardButton(text=times[0], callback_data='ninetoten'), 
                InlineKeyboardButton(text=times[1], callback_data='tentoeleven'),
                InlineKeyboardButton(text=times[2], callback_data='eleventotwelve'),
                InlineKeyboardButton(text=times[3], callback_data='twelvetothirteen'),
                InlineKeyboardButton(text=times[4], callback_data='thirteentofourteen'),
                InlineKeyboardButton(text=times[5], callback_data='fourteentofifteen'),
]

recieve_document_kb = ReplyKeyboardMarkup(resize_keyboard = True)
recieve_document_kb.add(KeyboardButton('/Receive_Document'))

reactivate_kb = ReplyKeyboardMarkup(resize_keyboard=True)
reactivate_kb.add(KeyboardButton('/Reactivate_bot'))


def get_ikb() -> InlineKeyboardMarkup:
    global collecton_ikb

    ikb = InlineKeyboardMarkup(row_width=2)

    washers = free_washers()

    for i in range(0, 6):
        for time in times:
            if any(washers[i]['time'][time] == True):
                print(i)
                ikb1 = collecton_ikb[i]
                ikb.add(ikb1)
                break
            else:
                continue

    return ikb