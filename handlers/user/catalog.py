from filters import IsUser
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.types.chat import ChatActions

from keyboards.inline.calendar_inline import calendar_markup
from keyboards.inline.calendar_inline import date_cb
from keyboards.inline.categories import categories_markup
from .menu import catalog
from loader import dp, db, bot
from keyboards.inline.categories import category_cb
from keyboards.inline.products_from_catalog import product_markup
from keyboards.inline.products_from_catalog import product_cb
from keyboards.default.markups import *
from app import process_settings
from aiogram.types import ContentType
from keyboards.inline.calendar_inline import calendar_markup
from keyboards.inline.calendar_inline import date_cb

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.types.chat import ChatActions
from aiogram.types import ReplyKeyboardMarkup
from datetime import datetime, date, timedelta


@dp.callback_query_handler(IsUser(), category_cb.filter(id='55555'))
async def todo_callback_handler(query: CallbackQuery, callback_data: dict):
    products = db.fetchall('''SELECT * FROM products product
        WHERE product.tag != ? AND product.tag != ?
        ORDER BY price ASC
        LIMIT 5''', ('Schedule', 'Event',))
    await query.message.delete()
    await show_products(query.message, products)

@dp.callback_query_handler(IsUser(), category_cb.filter(id='111111'))
async def schedule_callback_handler(query: CallbackQuery, callback_data: dict):

    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Today', callback_data=date_cb.new(id='0', action='today'))
    btn2 = InlineKeyboardButton('Tomorrow', callback_data=date_cb.new(id='0', action='tomorrow'))
    btn3 = InlineKeyboardButton('Calendar', callback_data=date_cb.new(id='0', action='calendar'))
    markup.row(btn1, btn2, btn3)
    await query.message.delete()
    await query.message.answer(text='Map for university', reply_markup=markup)

@dp.callback_query_handler(IsUser(), date_cb.filter(action='today'))
async def map_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    today_str = date.today().strftime('%Y-%m-%d')
    subjects = db.fetchone('''SELECT subjects FROM calendar
    WHERE date_id = ?''',(today_str,))[0]
    products = db.fetchall('''SELECT * FROM products product
        WHERE product.tag = ? OR product.tag = ?''', ('Schedule', 'Event',))
    await query.message.delete()
    await show_subject(query.message, products, subject_lst=subjects, date_str=today_str)


@dp.callback_query_handler(IsUser(), date_cb.filter(action='tomorrow'))
async def map_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    tomorrow = date.today() + timedelta(days=1)
    today_str = tomorrow.strftime('%Y-%m-%d')
    subjects = db.fetchone('''SELECT subjects FROM calendar
    WHERE date_id = ?''',(today_str,))[0]
    products = db.fetchall('''SELECT * FROM products product
        WHERE product.tag = ? OR product.tag = ?''', ('Schedule', 'Event',))
    await query.message.delete()
    await show_subject(query.message, products, subject_lst=subjects, date_str=today_str)


@dp.callback_query_handler(IsUser(), date_cb.filter(action='calendar'))
async def map_callback_handler(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer('Datetime?', reply_markup=calendar_markup())


month = datetime.now().month
year = datetime.now().year


@dp.callback_query_handler(IsUser(), date_cb.filter())
async def calendar_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    global month, year
    async with state.proxy() as data:
        if callback_data['action'] == 'increase':
            month += 1
            if month == 13:
                month = 1
                year += 1
            await query.message.edit_reply_markup(calendar_markup(month_int=month, year_int=year))
        elif callback_data['action'] == 'decrease':
            month -= 1
            if month == 0:
                month = 12
                year -= 1
            await query.message.edit_reply_markup(calendar_markup(month_int=month, year_int=year))
        else:
            date_data = callback_data['action'].split()
            tomorrow = date(year, month, int(date_data[0]))
            today_str = tomorrow.strftime('%Y-%m-%d')
            subjects = db.fetchone('''SELECT subjects FROM calendar
            WHERE date_id = ?''', (today_str,))[0]
            products = db.fetchall('''SELECT * FROM products product
            WHERE product.tag = ?''', ('Schedule',))
            await query.message.delete()
            await show_subject(query.message, products, subject_lst=subjects)
            #await state.update_data(category_index=category_idx)


user_message = 'Task list'
admin_message = 'New task'


async def show_subject(m, products, subject_lst='', date_str='2023-09-27'):
    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)
    s = 0
    for idx, title, body, price, time, tag in products:
        if idx in subject_lst.split(';'):
            text = f'<b>{title}</b>\n\n{body}\n\nTime: {time}.'
            s += 1
            await m.answer(text,)
        if price == date_str and tag == 'Event':
            text = f'<b>{title}</b>\n\n{body}\n\nTime: {time}.'
            s += 1
            await m.answer(text,)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(user_message, admin_message)
    if s == 0:
        await m.answer('Event list is empty',
                       reply_markup=markup)


@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict):

    products = db.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=?) 
    AND product.idx NOT IN (SELECT idx FROM cart WHERE cid = ?)''',
                           (callback_data['id'], query.message.chat.id))

    await query.answer('Список мероприятий')
    await show_products(query.message, products)


@dp.message_handler(IsUser(), text=catalog)
async def process_catalog(message: Message):
    await message.answer('Выберите раздел, чтобы вывести список товаров:',
                         reply_markup=categories_markup())


async def show_products(m, products):
    
    if len(products) == 0:
        await m.answer('Здесь ничего нет 😢')
    else:
        await bot.send_chat_action(m.chat.id, ChatActions.TYPING)
        d = ['',' Января', ' Февраля', " Марта", " Апреля", " Мая", " Июня", " Июля", " Августа",
             " Сентября", " Октября", " Ноября", " Декабря"]
        for idx, title, body, price, time, tag in products:
            date_lst = price.split('-')
            date_str = date_lst[-1] + ' ' + d[int(date_lst[1])]
            if tag == 'Event':
                if date.today().strftime('%Y-%m-%d') < price:
                    #await m.answer(text, reply_markup=markup)
                    text = f'<b>{title}</b>\n\n{body}\nDeadline: {date_str}.'
                    #await m.answer(text, reply_markup=markup)
                    await m.answer(text,)
            else:
                markup = InlineKeyboardMarkup()

                markup.add(InlineKeyboardButton('✅ Сделано', callback_data=product_cb.new(id=idx, action='delete')))
                text = f'<b>{title}</b>\n{body}\nDeadline: {date_str}.'
                #await m.answer(text, )
                await m.answer(text, reply_markup=markup)


@dp.callback_query_handler(IsUser(), product_cb.filter(action='delete'))
async def delete_product_callback_handler(query: CallbackQuery,
                                          callback_data: dict):
    product_idx = callback_data['id']
    db.query('DELETE FROM products WHERE idx=?', (product_idx,))
    await query.answer('Nice!')
    await query.message.delete()


@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: CallbackQuery,
                                       callback_data: dict):
    db.query('INSERT INTO cart VALUES (?, ?, 1)',
             (query.message.chat.id, callback_data['id']))

    await query.answer('Товар добавлен в корзину!')
    await query.message.delete()
