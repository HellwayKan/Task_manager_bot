from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from datetime import datetime
import calendar

date_cb = CallbackData('date', 'id', 'action')


def calendar_markup(idx='0', month_int=datetime.now().month, year_int=datetime.now().year):
    global date_cb

    markup = InlineKeyboardMarkup()
    month = month_int
    year = year_int

    year_month_btn = InlineKeyboardButton(f'{year}/{month}', callback_data=date_cb.new(id=idx,action='y/m'))
    back_btn = InlineKeyboardButton('⬅️', callback_data=date_cb.new(id=idx,action='decrease'))
    next_btn = InlineKeyboardButton('➡️', callback_data=date_cb.new(id=idx,action='increase'))
    markup.row(back_btn, year_month_btn, next_btn)

    d1 = InlineKeyboardButton('Mon ', callback_data=date_cb.new(id=idx,action='view'))
    d2 = InlineKeyboardButton('Tue', callback_data=date_cb.new(id=idx,action='view'))
    d3 = InlineKeyboardButton('Wed ', callback_data=date_cb.new(id=idx,action='view'))
    d4 = InlineKeyboardButton('Tru', callback_data=date_cb.new(id=idx,action='view'))
    d5 = InlineKeyboardButton('Fri', callback_data=date_cb.new(id=idx,action='view'))
    d6 = InlineKeyboardButton('Sat', callback_data=date_cb.new(id=idx,action='view'))
    d7 = InlineKeyboardButton('Sun', callback_data=date_cb.new(id=idx,action='view'))
    markup.row(d1,d2,d3,d4,d5,d6,d7)

    c = calendar.Calendar()
    d = [' Января',' Февраля'," Марта"," Апреля"," Мая"," Июня"," Июля"," Августа",
         " Сентября", " Октября", " Ноября", " Декабря"]
    lis = c.monthdayscalendar(year, month)
    for i in range(len(lis)):

        dd1 = InlineKeyboardButton(str(lis[i][0]), callback_data=date_cb.new(id=idx,action=str(lis[i][0])+d[month-1]))
        dd2 = InlineKeyboardButton(str(lis[i][1]), callback_data=date_cb.new(id=idx,action=str(lis[i][1])+d[month-1]))
        dd3 = InlineKeyboardButton(str(lis[i][2]), callback_data=date_cb.new(id=idx,action=str(lis[i][2])+d[month-1]))
        dd4 = InlineKeyboardButton(str(lis[i][3]), callback_data=date_cb.new(id=idx,action=str(lis[i][3])+d[month-1]))
        dd5 = InlineKeyboardButton(str(lis[i][4]), callback_data=date_cb.new(id=idx,action=str(lis[i][4])+d[month-1]))
        dd6 = InlineKeyboardButton(str(lis[i][5]), callback_data=date_cb.new(id=idx,action=str(lis[i][5])+d[month-1]))
        dd7 = InlineKeyboardButton(str(lis[i][6]), callback_data=date_cb.new(id=idx,action=str(lis[i][6])+d[month-1]))
        markup.row(dd1, dd2, dd3, dd4, dd5, dd6, dd7)

    return markup

