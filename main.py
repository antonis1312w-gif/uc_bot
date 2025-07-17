import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '8027439631:AAH_AxGFohBUqb7waZxR0zhSy2TnVO6BxyU'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

ADMIN_ID = 123456789  # Замени на свой ID
GUARANTOR_USERNAME = '@UCMANA9ER'

wallets = {
    'TON': 'UQA1l0gtL3gxHJM1MEEfv7piyplekfA5nh_1J0eiwdjrWXN9',
    'USDT (TRC-20)': 'TP9mhRQpbT1QuAs8pvYAZjf4gNRZvJExzm',
    'USDT (ERC-20)': '0x55dB9b289d2f28912fe7bEb16F9614a364F14080'
}

LANGUAGES = {
    "en": {
        "start": "Welcome to Fragchange bot!\nSelect action:",
        "buy": "Buy Username",
        "sell": "Sell Username",
        "language": "Change Language",
        "select_currency": "Select currency:",
        "enter_price": "Enter the price (min 5 TON):",
        "confirm_sell": "Your request has been sent to the guarantor.",
        "not_enough": "Minimum amount is 5 TON.",
    },
    "ru": {
        "start": "Добро пожаловать в Fragchange бот!\nВыберите действие:",
        "buy": "Купить юзернейм",
        "sell": "Продать юзернейм",
        "language": "Сменить язык",
        "select_currency": "Выберите валюту:",
        "enter_price": "Введите цену (минимум 5 TON):",
        "confirm_sell": "Заявка отправлена гаранту.",
        "not_enough": "Минимальная сумма — 5 TON.",
    },
}

user_lang = {}

class SellFSM(StatesGroup):
    choosing_currency = State()
    entering_price = State()

def get_text(user_id, key):
    lang = user_lang.get(user_id, "en")
    return LANGUAGES[lang].get(key, key)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(get_text(message.from_user.id, "buy")))
    kb.add(KeyboardButton(get_text(message.from_user.id, "sell")))
    kb.add(KeyboardButton(get_text(message.from_user.id, "language")))
    await message.answer(get_text(message.from_user.id, "start"), reply_markup=kb)

@dp.message_handler(Text(equals=["Sell Username", "Продать юзернейм"]))
async def start_sell(message: types.Message):
    await message.answer(get_text(message.from_user.id, "select_currency"))
    await SellFSM.choosing_currency.set()

@dp.message_handler(state=SellFSM.choosing_currency)
async def choose_currency(message: types.Message, state: FSMContext):
    if message.text not in wallets:
        return await message.answer(get_text(message.from_user.id, "select_currency"))
    await state.update_data(currency=message.text)
    await message.answer(get_text(message.from_user.id, "enter_price"))
    await SellFSM.entering_price.set()

@dp.message_handler(state=SellFSM.entering_price)
async def enter_price(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount < 5:
            await message.answer(get_text(message.from_user.id, "not_enough"))
            return
    except ValueError:
        return await message.answer(get_text(message.from_user.id, "enter_price"))

    data = await state.get_data()
    currency = data["currency"]
    wallet = wallets[currency]
    await message.answer(f"{get_text(message.from_user.id, 'confirm_sell')}\n"
                         f"Send payment to: `{wallet}`", parse_mode="Markdown")
    await state.finish()

@dp.message_handler(Text(equals=["Change Language", "Сменить язык"]))
async def change_lang(message: types.Message):
    current = user_lang.get(message.from_user.id, "en")
    new_lang = "ru" if current == "en" else "en"
    user_lang[message.from_user.id] = new_lang
    await cmd_start(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
