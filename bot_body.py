from lib.configs import *
from lib.keyboards import *
from lib.db_utils import *

from sqlalchemy.exc import IntegrityError

from aiogram import Dispatcher, executor, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, LabeledPrice

bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    await message.answer(f"Здравствуйте <b>{message.from_user.full_name}</b>"
                         f"\nВас приветствует бот доставки micros")
    await register_user(message)


async def register_user(message: Message):
    """Проверка пользователя"""
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    user = db_check_user(chat_id)

    if user:
        await message.answer('Авторизация прошла успешно')
        await show_main_menu(message)
    else:
        db_register_user(full_name, chat_id)
        await message.answer(
            "Для связи с Вами нам нужен Ваш контактный номер",
            reply_markup=share_phone_button()
        )


@dp.message_handler(content_types=['contact'])
async def finish_register(message: Message):
    """Обновление данных пользователя"""
    chat_id = message.chat.id
    phone = message.contact.phone_number
    db_update_user(chat_id, phone)
    await create_cart_for_user(message)
    await message.answer("Регистрация прошла успешно")
    await show_main_menu(message)


async def create_cart_for_user(message: Message):
    """Создание временной корзинки пользователя"""
    chat_id = message.chat.id
    try:
        db_create_user_cart(chat_id)
    except IntegrityError:
        ...


async def show_main_menu(message: Message):
    """Основное меню, Reply кнопки"""
    await message.answer("Выберите направление", reply_markup=generate_main_menu())


@dp.message_handler(lambda message: '✔ Сделать заказ' in message.text)
async def make_order(message: Message):
    chat_id = message.chat.id
    # TODO Получить id корзинки
    await bot.send_message(chat_id, "Погнали", reply_markup=back_to_main_menu())
    await message.answer("Выберите категорию:", reply_markup=generate_category_menu())


@dp.callback_query_handler(lambda call: 'category_' in call.data)
async def show_product_button(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    category_id = int(call.data.split('_')[-1])
    await bot.edit_message_text(
        "Выберите продукт:",
        chat_id,
        message_id,
        reply_markup=show_product_by_category(category_id)
    )






executor.start_polling(dp)
