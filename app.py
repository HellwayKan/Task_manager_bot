from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove
from aiogram import executor
from logging import basicConfig, INFO

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from data.config import ADMINS
from loader import dp, db, bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import handlers


user_message = 'Task list'
admin_message = 'New task'
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(user_message, admin_message)

    await message.answer('''Good day! Let's start check our tasks.
    ''', reply_markup=markup)


category_cb = CallbackData('category', 'id', 'action')


@dp.message_handler(text=admin_message)
async def process_settings(message: Message):
    cid = message.chat.id
    if cid not in ADMINS:
        ADMINS.append(cid)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Schedule', callback_data=category_cb.new(id='111111', action='schedule')))
    for idx, title in db.fetchall('SELECT * FROM categories'):
        markup.add(InlineKeyboardButton(title, callback_data=category_cb.new(id=idx, action='view')))

    markup.add(InlineKeyboardButton('+ Добавить категорию', callback_data='add_category'))

    markup1 = ReplyKeyboardMarkup(resize_keyboard=True)
    markup1.row(user_message, admin_message)

    await message.answer('Настройка категорий:', reply_markup=markup)
    await message.answer('📋⬆️', reply_markup=markup1)


@dp.message_handler(text=user_message)
async def user_mode(message: types.Message):
    cid = message.chat.id
    if cid in ADMINS:
        ADMINS.remove(cid)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Schedule', callback_data=category_cb.new(id='111111', action='schedule')))
    markup.add(InlineKeyboardButton('To do soon', callback_data=category_cb.new(id='55555', action='todosoon')))
    for idx, title in db.fetchall('SELECT * FROM categories'):
        markup.add(InlineKeyboardButton(title, callback_data=category_cb.new(id=idx, action='view')))
    await message.answer('Включен пользовательский режим.',
                         reply_markup=markup)


async def on_startup(dp):
    basicConfig(level=INFO)
    db.create_tables()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
