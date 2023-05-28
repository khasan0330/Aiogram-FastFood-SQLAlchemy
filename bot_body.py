from lib.configs import *
from lib.keyboards import *
from lib.db_utils import *

from sqlalchemy.exc import IntegrityError

from aiogram import Dispatcher, executor, Bot
from aiogram.types import Message, CallbackQuery, InputMedia, ReplyKeyboardRemove, LabeledPrice

bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    await message.answer(
        f"Здравствуйте <b>{message.from_user.full_name}</b>"
        f"\nВас приветствует бот доставки micros"
    )
    await register_user(message)


async def register_user(message: Message):
    """Проверка пользователя"""
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    user = db_check_user(chat_id)

    if user:
        await message.answer(text='Авторизация прошла успешно')
        await show_main_menu(message)
    else:
        db_register_user(full_name, chat_id)
        await message.answer(
            text="Для связи с Вами нам нужен Ваш контактный номер",
            reply_markup=share_phone_button()
        )


@dp.message_handler(content_types=['contact'])
async def finish_register(message: Message):
    """Обновление данных пользователя"""
    chat_id = message.chat.id
    phone = message.contact.phone_number
    db_update_user(chat_id, phone)
    await create_cart_for_user(message)
    await message.answer(text="Регистрация прошла успешно")
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
    await message.answer(
        text="Выберите направление",
        reply_markup=generate_main_menu()
    )


@dp.message_handler(lambda message: '✔ Сделать заказ' in message.text)
async def make_order(message: Message):
    chat_id = message.chat.id
    await bot.send_message(
        chat_id=chat_id,
        text="Погнали",
        reply_markup=back_to_main_menu()
    )
    await message.answer(
        text="Выберите категорию:",
        reply_markup=generate_category_menu(chat_id)
    )


@dp.callback_query_handler(lambda call: 'category_' in call.data)
async def show_product_button(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    category_id = int(call.data.split('_')[-1])
    await bot.edit_message_text(
        text="Выберите продукт:",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=show_product_by_category(category_id)
    )


@dp.callback_query_handler(lambda call: 'main_menu' in call.data)
async def return_to_category(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Выберите категорию:",
        reply_markup=generate_category_menu(chat_id)
    )


@dp.message_handler(regexp=r'Главное меню')
async def return_to_main_menu(message: Message):
    message_id = message.message_id - 1
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    await show_main_menu(message)


@dp.callback_query_handler(lambda call: 'product_' in call.data)
async def show_choose_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )
    product_id = int(call.data.split('_')[-1])
    product = db_get_product(product_id)

    user_cart = db_get_user_cart(chat_id)
    db_update_to_cart(price=product.price, quantity=1, cart_id=user_cart.cart_id)
    await bot.send_message(
        chat_id=chat_id,
        text='Выберите модификатор',
        reply_markup=back_to_menu()
    )

    text = f"{product.product_name}\n"
    text += f"Ингредиенты: {product.description}\n"
    text += f"Цена: {product.price} сум"

    with open(product.image, mode='rb') as img:
        await bot.send_photo(
            chat_id=chat_id,
            photo=img,
            caption=text,
            reply_markup=generate_constructor_button(1)
        )


@dp.callback_query_handler(lambda call: 'action' in call.data)
async def constructor_changes(call: CallbackQuery):
    chat_id = call.from_user.id
    message_id = call.message.message_id
    action = call.data.split()[-1]
    try:
        user_cart = db_get_user_cart(chat_id)
        cart_id = user_cart.cart_id
        total_products = user_cart.total_products
    except Exception as e:
        print(e, '===================ERROR==========')
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
        await bot.send_message(
            chat_id=chat_id,
            text="К сожалению вы еще не отправили нам контакт",
            reply_markup=share_phone_button()
        )

    product_name = call.message['caption'].split('\n')[0]
    product = db_get_product_by_name(product_name)
    match action:
        case '+':
            db_update_to_cart(
                price=product.price,
                quantity=total_products + 1,
                cart_id=cart_id
            )
        case '-':
            db_update_to_cart(
                price=product.price,
                quantity=total_products - 1,
                cart_id=cart_id
            )

    user_cart = db_get_user_cart(chat_id)
    text = f"{product.product_name}\n"
    text += f"Ингредиенты: {product.description}\n"
    text += f"Цена: {user_cart.total_price} сум"

    try:
        with open(product.image, mode='rb') as img:
            await bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=InputMedia(media=img, caption=text),
                reply_markup=generate_constructor_button(user_cart.total_products)
            )
    except:
        pass


@dp.message_handler(regexp=r'⬅ Назад')
async def return_menu(message: Message):
    message_id = message.message_id - 1
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    await make_order(message)


@dp.callback_query_handler(lambda call: 'put into cart' in call.data)
async def put_into_cart(call: CallbackQuery):
    chat_id = call.from_user.id
    user_cart = db_get_user_cart(chat_id)
    cart_id = user_cart.cart_id
    total_products = user_cart.total_products
    total_price = user_cart.total_price
    product_name = call.message['caption'].split('\n')[0]

    if db_ins_or_upd_finally_cart(cart_id, product_name, total_products, total_price):
        await bot.answer_callback_query(call.id, "Продукт успешно добавлен")
    else:
        await bot.answer_callback_query(call.id, "Количество успешно изменено")


@dp.callback_query_handler(regexp=r"Ваша корзинка")
async def show_finally_cart(call: CallbackQuery):
    message_id = call.message.message_id
    chat_id = call.from_user.id
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )

    cart_products = db_get_cart_products(chat_id)
    text = 'Ваша корзина: \n\n'
    total_products = total_price = count = 0
    for name, quantity, price in cart_products:
        count += 1
        total_products += quantity
        total_price += price
        text += f'{count}. {name}\nКоличество: {quantity}\nОбщая стоимость: {price}\n\n'

    if count:
        text += f'Общее количество продуктов: {total_products}\nОбщая стоимость корзины: {total_price}'
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=generate_cart_button(chat_id)
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="Ваша корзинка пуста 🥴"
        )





executor.start_polling(dp)
