from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loader import dp, db, bot
from aiogram import executor





# dun_w это префикс, его можно ловить и стандартным text_startswith=...
cd_walk = CallbackData("dun_w", "action", "floor")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(f"Налево",
                             callback_data=cd_walk.new(
                                 action='1',
                                 floor=2
                             )),
        InlineKeyboardButton(f"Направо",
                             callback_data=cd_walk.new(
                                 action='2',
                                 floor=2
                             ))
    )
    await message.answer("text", reply_markup=markup)


@dp.callback_query_handler(cd_walk.filter())
async def button_press(call: types.CallbackQuery, callback_data: dict):
    action = callback_data.get('action')  # 1 or 2
    floor = callback_data.get('floor')  # 2


if __name__ == '__main__':
    d = ['Января','Февраля',"Марта","Апреля","Мая","Июня","Июля","Августа", "Сентября", "Октября", "Ноября", "Декабря"]
    d = dict(enumerate(d, start=1))
    #executor.start_polling(dp, skip_updates=True)
    print(d[1])