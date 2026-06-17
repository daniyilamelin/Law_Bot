import os
from dotenv import load_dotenv
from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from aiogram.filters import StateFilter

offer = Router()
load_dotenv()
CATEGORIES = {
    "f_cyvil": "Цивільне право",
    "f_work": "Трудові суперечки",
    "f_police": "Штрафи/поліція",
    "f_family": "Сімейні питання",
    "f_peace": "Договори",
    "f_law": "Судова допомога",
    "f_other": "Інше (зазначити в описі)"
}

class Add_Offer(StatesGroup):
    id = State()
    name = State()
    phone = State()
    category = State()
    description = State()
    goal = State()
    check = State()

    up_name = State()
    up_phone = State()
    up_description = State()
    up_goal = State()

async def show(message: Message, state:FSMContext):
    choice = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text = "Так , звичайно", callback_data = "yes")
            ],
            [
                InlineKeyboardButton(text = "Ні , ще подумаю над зверненням", callback_data = "no")
            ],
        ]
    )
    data = await state.get_data()
    await message.answer(
            "Ось ваша заява\n"
            f"📝 Нова заява!\n"
            f"👤 Ім'я: {data['name']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"📂 Категорія: {data['category']}\n"
            f"🧾 Опис: {data['description']}\n"
            f"🎯 Мета звернення: {data['goal']}\n"
                        "Дякуємо за заповнення форми.\n"
                         "Можемо надіслати заявку на розгляд нашим фахівцям?", reply_markup= choice)

@offer.message(Command("start"))
async def start(message: Message):
    await message.answer("Вітаємо до бота Burmystrov&Partners.\n" 
    "Почніть заповнення заявки командою /help_me")


@offer.message(Command("help_me"))
async def procces(message: Message, state: FSMContext):
    await state.update_data(id = message.from_user.id)
    await state.set_state(Add_Offer.name)
    await message.answer("Гаразд, давайте почнемо реєстрацію. Вкажіть ваше ПІБ")

@offer.message(Add_Offer.name)
async def phone(message: Message, state : FSMContext):
    await state.update_data(name = message.text)
    await state.set_state(Add_Offer.phone)
    await message.answer("ПІБ внесено, введіть ваш номер телефону")

@offer.message(Add_Offer.phone)
async def category(message: Message, state: FSMContext):
    await state.update_data(phone = message.text)
    await state.set_state(Add_Offer.category)
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text = "Цивільні правовідносини", callback_data = "f_cyvil")
            ],
            [
                InlineKeyboardButton(text = "Трудові суперечки", callback_data = "f_work")
            ],
            [
                InlineKeyboardButton(text = "Штрафи/поліція", callback_data = "f_police")
            ],
            [
                InlineKeyboardButton(text = "Сімейне право", callback_data = "f_family")
            ],
            [
                InlineKeyboardButton(text = "Договори", callback_data = "f_peace")
            ],
            [
                InlineKeyboardButton(text = "Правова допомога", callback_data = "f_law")
            ],
            [
                InlineKeyboardButton(text = "Інше (зазначити в описі)", callback_data = "f_other")
            ],

        ]
    )
    await message.answer("Виберіть категорію в якій вам потрібна допомога", reply_markup = inline_kb)

@offer.callback_query(F.data.startswith("f_"), Add_Offer.category)
async def description(callback: CallbackQuery, state= FSMContext):
    category = CATEGORIES.get(callback.data)
    await state.update_data(category = category)
    await state.set_state(Add_Offer.description)
    await callback.message.answer("Категорію вибрано. Напишіть короткий опис ситуації")

@offer.message(Add_Offer.description)
async def goal(message: Message, state : FSMContext):
    await state.update_data(description = message.text)
    await state.set_state(Add_Offer.goal)
    await message.answer("Дякуємо за опис. Введіть мету звернення")


@offer.message(Add_Offer.goal)
async def final(message: Message, state : FSMContext):
    await state.update_data(goal = message.text)
    await show(message, state)


@offer.callback_query(F.data.startswith("yes"))
async def prints(callback: CallbackQuery, state: FSMContext, bot: Bot):
    
    await callback.message.answer("Наші фахівці обов'язково зв'яжуться з вами. Очікуйте на звернення\n")
    data = await state.get_data()
    admins = os.getenv("admins")
    for a in admins:
        await bot.send_message(
            a, 
            f"📝 Нова заява!\n"
            f"💬  ID: {data['id']}\n "
            f"👤 Ім'я: {data['name']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"📂 Категорія: {data['category']}\n"
            f"🧾 Опис: {data['description']}\n"
            f"🎯 Мета звернення: {data['goal']}"            
        )

@offer.callback_query(F.data.startswith("no"))
async def choose_change_something(callback: CallbackQuery):
    inl_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text = "Ім'я", callback_data = "fill_name")
            ],
            [
                InlineKeyboardButton(text = "Телефон", callback_data = "fill_phone")
            ],
            [
                InlineKeyboardButton(text = "Категорія", callback_data = "fill_category")
            ],
            [
                InlineKeyboardButton(text = "Опис", callback_data = "fill_description")
            ],
            [
                InlineKeyboardButton(text = "Мета", callback_data = "fill_goal")
            ],
        ]
    )
    await callback.message.answer("Яку частину форми ви б хотіли змінити ?", reply_markup= inl_kb)

@offer.callback_query(F.data.startswith("fill_"))
async def change_something(callback: CallbackQuery, state: FSMContext):
    chose = callback.data.split("_", 1)
    field = chose[1]
    states_map = {
        'name': Add_Offer.up_name,
        'phone': Add_Offer.up_phone,
        'description': Add_Offer.up_description,
        'goal': Add_Offer.up_goal,
    }


    if field == 'category':
        await state.set_state(Add_Offer.category)
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[
            [
                InlineKeyboardButton(text = "Цивільні правовідносини", callback_data = "catt_cyvil")
            ],
            [
                InlineKeyboardButton(text = "Трудові суперечки", callback_data = "catt_work")
            ],
            [
                InlineKeyboardButton(text = "Штрафи/поліція", callback_data = "catt_police")
            ],
            [
                InlineKeyboardButton(text = "Сімейне право", callback_data = "catt_family")
            ],
            [
                InlineKeyboardButton(text = "Договори", callback_data = "catt_peace")
            ],
            [
                InlineKeyboardButton(text = "Правова допомога", callback_data = "catt_law")
            ],
            [
                InlineKeyboardButton(text = "Інше (зазначити в описі)", callback_data = "catt_other")
            ],

            ]
        )
        await callback.message.answer("Виберіть категорію в якій вам потрібна допомога", reply_markup = inline_kb)
    else:
        await state.set_state(states_map[field])
        await callback.message.answer("Будь ласка , введіть нову інформацію")


@offer.callback_query(F.data.startswith("catt_"))
async def new_category(callback: CallbackQuery, state:FSMContext):
    CATEGOR = {
    "catt_cyvil": "Цивільне право",
    "catt_work": "Трудові суперечки",
    "catt_police": "Штрафи/поліція",
    "catt_family": "Сімейні питання",
    "catt_peace": "Договори",
    "catt_law": "Судова допомога",
    "catt_other": "Інше (зазначити в описі)"
    }
    category = CATEGOR.get(callback.data)

    await state.update_data(category = category)
    choice = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text = "Так , звичайно", callback_data = "yes")
            ],
            [
                InlineKeyboardButton(text = "Ні , ще подумаю над зверненням", callback_data = "no")
            ],
        ]
    )
    data = await state.get_data()
    await callback.message.answer(
            "Ось ваша заява"
            f"📝 Нова заява!\n"
            f"👤 Ім'я: {data['name']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"📂 Категорія: {data['category']}\n"
            f"🧾 Опис: {data['description']}\n"
            f"🎯 Мета звернення: {data['goal']}\n"
                        "Дякуємо за заповнення форми.\n"
                         "Можемо надіслати заявку на розгляд нашим фахівцям?", reply_markup= choice)
    

@offer.message(Add_Offer.up_name)
async def change_name(message: Message, state:FSMContext):
    await state.update_data(name = message.text)
    await show(message, state)

@offer.message(Add_Offer.up_phone)
async def change_phone(message: Message, state:FSMContext):
    await state.update_data(phone = message.text)
    await show(message, state)

@offer.message(Add_Offer.up_description)
async def change_description(message: Message, state:FSMContext):
    await state.update_data(description = message.text)
    await show(message, state)

@offer.message(Add_Offer.up_goal)
async def change_goal(message: Message, state:FSMContext):
    await state.update_data(goal = message.text)
    await show(message, state)    