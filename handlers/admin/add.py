from loader import dp, db, bot
from filters import IsAdmin
from handlers.user.menu import settings
from states import CategoryState
from states import ProductState
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
from hashlib import md5

category_cb = CallbackData('category', 'id', 'action')
date_cb = CallbackData('date', 'id', 'action')

'''
@dp.message_handler(IsAdmin(), text=settings)
async def process_settings(message: Message):

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Schedule', callback_data=category_cb.new(id='111111', action='schedule')))
    for idx, title in db.fetchall('SELECT * FROM categories'):

        markup.add(InlineKeyboardButton(title, callback_data=category_cb.new(id=idx, action='view')))

    markup.add(InlineKeyboardButton('+ Добавить категорию', callback_data='add_category'))

    await message.answer('Настройка категорий:', reply_markup=markup)
''' #add category first version

@dp.callback_query_handler(IsAdmin(), text='add_category')
async def add_category_callback_handler(query: CallbackQuery):
    await query.message.delete()
    await query.message.answer('Название категории?')
    await CategoryState.title.set()


@dp.message_handler(IsAdmin(), state=CategoryState.title)
async def set_category_title_handler(message: Message, state: FSMContext):

    category = message.text
    if category == 'Second':
        idx = '3652023'
    else:
        idx = md5(category.encode('utf-8')).hexdigest()
    db.query('INSERT INTO categories VALUES (?, ?)', (idx, category))

    await state.finish()
    await process_settings(message)


@dp.callback_query_handler(IsAdmin(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict,
                                    state: FSMContext):
    category_idx = callback_data['id']

    products = db.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=?)''',
                           (category_idx,))

    await query.message.delete()
    await query.answer('Все добавленные товары в эту категорию.')
    await state.update_data(category_index=category_idx)
    await show_products(query.message, products, category_idx)


#'''
@dp.callback_query_handler(category_cb.filter(id='111111'))
async def schedule_callback_handler(query: CallbackQuery, callback_data: dict):

    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Today', callback_data=date_cb.new(id='0', action='today'))
    btn2 = InlineKeyboardButton('Tomorrow', callback_data=date_cb.new(id='0', action='tomorrow'))
    btn3 = InlineKeyboardButton('Calendar', callback_data=date_cb.new(id='0', action='calendar'))
    markup.row(btn1, btn2, btn3)
    await query.message.delete()
    await query.message.answer(text='Map for university', reply_markup=markup)

@dp.callback_query_handler(IsAdmin(), date_cb.filter(action='today'))
async def map_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    today_str = date.today().strftime('%Y-%m-%d')
    subjects = db.fetchone('''SELECT subjects FROM calendar
    WHERE date_id = ?''',(today_str,))[0]
    products = db.fetchall('''SELECT * FROM products product
        WHERE product.tag = ? OR product.tag = ?''', ('Schedule', 'Event',))
    await query.message.delete()
    await show_subject(query.message, products, subject_lst=subjects, date_str=today_str)


@dp.callback_query_handler(IsAdmin(), date_cb.filter(action='tomorrow'))
async def map_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):
    tomorrow = date.today() + timedelta(days=1)
    today_str = tomorrow.strftime('%Y-%m-%d')
    subjects = db.fetchone('''SELECT subjects FROM calendar
    WHERE date_id = ?''',(today_str,))[0]
    products = db.fetchall('''SELECT * FROM products product
        WHERE product.tag = ? OR product.tag = ?''', ('Schedule', 'Event',))
    await query.message.delete()
    await show_subject(query.message, products, subject_lst=subjects, date_str=today_str)

@dp.callback_query_handler(IsAdmin(), date_cb.filter(action='calendar'))
async def map_callback_handler(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer('Datetime?', reply_markup=calendar_markup())
#'''
@dp.callback_query_handler(date_cb.filter())
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

#'''


cancel_message = '🚫 Отменить'
product_cb = CallbackData('product', 'id', 'action')
add_product = '➕ Добавить задачу'
delete_category = '🗑️ Удалить категорию'
user_message = 'Task list'
admin_message = 'New task'

async def show_subject(m, products, subject_lst, date_str='2023-09-27'):
    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)
    s = 0
    for idx, title, body, price, time, tag in products:
        if idx in subject_lst.split(';'):
            text = f'<b>{title}</b>\n\n{body}\n\nTime: {time}.'
            markup = InlineKeyboardMarkup()
            if IsAdmin():
                markup.add(
                    InlineKeyboardButton('🗑️ Удалить', callback_data=product_cb.new(id=idx, action='delete_subject')))
            s += 1
            await m.answer(text, reply_markup=markup)
        if price == date_str and tag == 'Event':
            text = f'<b>{title}</b>\n\n{body}\n\nTime: {time}.'
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton('🗑️ Удалить', callback_data=product_cb.new(id=idx, action='delete_subject')))
            s += 1
            await m.answer(text, reply_markup=markup)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(user_message, admin_message)
    if s == 0:
        await m.answer('Event list is empty',
                       reply_markup=markup)

    else:
        await m.answer('Хотите что-нибудь добавить или удалить?',
                   reply_markup=markup)


async def show_products(m, products, category_idx):
    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

    for idx, title, body, price, time, tag in products:

        text = f'<b>{title}</b>\n\n{body}\n\nDate: {price}\n\nTime: {time}.'
        markup = InlineKeyboardMarkup()

        markup.add(InlineKeyboardButton('🗑️ Удалить', callback_data=product_cb.new(id=idx, action='delete')))
        await m.answer(text, reply_markup=markup)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(add_product)

    if category_idx != 'a4ecfc70574394990cf17bd83df499f7':
        markup.add(delete_category)
    markup.add(user_message, admin_message)
    await m.answer('Хотите что-нибудь добавить или удалить?',
                   reply_markup=markup)


@dp.message_handler(IsAdmin(), text=delete_category)
async def delete_category_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if 'category_index' in data.keys():
            idx = data['category_index']

            db.query(
                'DELETE FROM products WHERE tag IN (SELECT '
                'title FROM categories WHERE idx=?)',
                (idx,))
            db.query('DELETE FROM categories WHERE idx=?', (idx,))

            await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
            await process_settings(message)


@dp.message_handler(IsAdmin(), text=add_product)
async def process_add_product(message: Message):
    await ProductState.title.set()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)

    await message.answer('Название?', reply_markup=markup)


@dp.message_handler(IsAdmin(), text=cancel_message, state=ProductState.title)
async def process_cancel(message: Message, state: FSMContext):
    await message.answer('Ок, отменено!', reply_markup=ReplyKeyboardRemove())
    await state.finish()

    await process_settings(message)


@dp.message_handler(IsAdmin(), state=ProductState.title)
async def process_title(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text

    await ProductState.next()
    await message.answer('Описание?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.body)
async def process_body_back(message: Message, state: FSMContext):
    await ProductState.title.set()
    async with state.proxy() as data:
        await message.answer(f"Изменить название с <b>{data['title']}</b>?",
                             reply_markup=back_markup())


@dp.message_handler(IsAdmin(), state=ProductState.body)
async def process_body(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['body'] = message.text

    await ProductState.next()
    await message.answer('Datetime?', reply_markup=calendar_markup())


month = datetime.now().month
year = datetime.now().year


@dp.callback_query_handler(date_cb.filter(), state=ProductState.price)
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
            data['price'] = date(year, month, int(date_data[0]))
            '''
            title = data['title']
            body = data['body']
            price = data['price']
            if data['category_index'] == '3652023':
                #data['time'] == '00 00'
                text = f'<b>{title}</b>\n\n{body}\n\nДата: {price.day}-{price.month}'
                await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=check_markup())
                await ProductState.confirm.set()
                #await ProductState.next()
                #await ProductState.next()
            else:'''
            text = 'Time?'

            await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=pass_markup())
            await ProductState.next()

#'''
@dp.message_handler(IsAdmin(), state=ProductState.time)
async def set_time(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
        title = data['title']
        body = data['body']
        price = data['price']
        time = data['time']

    text = f'<b>{title}</b>\n\n{body}\n\nДата: {price.day}-{price.month}\nTime: {time} '
    markup = check_markup()
    await message.answer(text=text, reply_markup=markup)
    await ProductState.next()
#'''

#'''
@dp.message_handler(IsAdmin(), text=all_right_message, state=ProductState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        title = data['title']
        body = data['body']
        price = data['price']
        time = data['time']

        tag = db.fetchone(
            'SELECT title FROM categories WHERE idx=?',
            (data['category_index'],))[0]
        idx = md5(' '.join([title, body, tag]
                           ).encode('utf-8')).hexdigest()
        db.query('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)',
                 (idx, title, body, price, time, tag))
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(user_message, admin_message)
    await state.finish()
    await message.answer('Готово!', reply_markup=markup)
    await process_settings(message)
   # scheduler.add_job(send_notifications, trigger='date',
      #run_date=datetime.now(), kwargs={'chat_id': message.from_user.id})


@dp.callback_query_handler(IsAdmin(), product_cb.filter(action='delete'))
async def delete_product_callback_handler(query: CallbackQuery,
                                          callback_data: dict):
    product_idx = callback_data['id']
    db.query('DELETE FROM products WHERE idx=?', (product_idx,))
    await query.answer('Удалено!')
    await query.message.delete()

'''
@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.confirm)
async def process_confirm_back(message: Message, state: FSMContext):
    await ProductState.price.set()

    async with state.proxy() as data:
        await message.answer(f"Изменить цену с <b>{data['price']}</b>?",
                             reply_markup=back_markup())

@dp.message_handler(IsAdmin(), content_types=ContentType.TEXT, state=ProductState.image)
async def process_image_url(message: Message, state: FSMContext):
    if message.text == back_message:
        await ProductState.body.set()
        async with state.proxy() as data:
            await message.answer(f"Изменить описание с <b>{data['body']}</b>?",
                                 reply_markup=back_markup())
    else:
        await message.answer('Вам нужно прислать фото товара.')

@dp.message_handler(IsAdmin(), lambda message: not message.text.isdigit(), state=ProductState.price)
async def process_price_invalid(message: Message, state: FSMContext):
    if message.text == back_message:
        await ProductState.image.set()
        async with state.proxy() as data:
            await message.answer("Другое изображение?",
                                 reply_markup=back_markup())
    else:
        await message.answer('Укажите цену в виде числа!')
'''


@dp.message_handler(IsAdmin(),
                    lambda message: message.text not in [back_message, all_right_message],
                    state=ProductState.confirm)
async def process_confirm_invalid(message: Message, state: FSMContext):
    await message.answer('Такого варианта не было.')

