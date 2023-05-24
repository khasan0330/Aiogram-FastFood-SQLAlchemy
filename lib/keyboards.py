from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup

from lib.db_utils import db_get_categories, db_get_products, db_get_final_price


def share_phone_button() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton(text="Отправить свой контакт", request_contact=True)]
    ], resize_keyboard=True)


def generate_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton(text="✔ Сделать заказ")],
        [
            KeyboardButton(text="📒 История"),
            KeyboardButton(text="🛒 Корзинка"),
            KeyboardButton(text="⚙ Настройки")
        ]
    ], resize_keyboard=True)


def back_to_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='Главное меню')]
    ], resize_keyboard=True)


def generate_category_menu(chat_id: int) -> InlineKeyboardMarkup:
    total_price = db_get_final_price(chat_id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(
            text=f'Ваша корзинка  ({total_price if total_price else 0} сум)',
            callback_data='Ваша корзинка'
        )
    )
    categories = db_get_categories()
    buttons = []
    for category in categories:
        bnt = InlineKeyboardButton(
            text=category.category_name,
            callback_data=f"category_{category.category_id}"
        )
        buttons.append(bnt)
    markup.add(*buttons)
    return markup


def show_product_by_category(category_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    products = db_get_products(category_id)
    buttons = []
    for product in products:
        btn = InlineKeyboardButton(
            text=product.product_name,
            callback_data=f"product_{product.category_id}"
        )
        buttons.append(btn)
    markup.add(*buttons)
    markup.row(
        InlineKeyboardButton(text="⬅ Назад", callback_data="main_menu")
    )
    return markup


def generate_constructor_button(quantity: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    buttons = [
        InlineKeyboardButton(text='➖', callback_data='action -'),
        InlineKeyboardButton(text=str(quantity), callback_data=str(quantity)),
        InlineKeyboardButton(text='➕', callback_data='action +'),
        InlineKeyboardButton(text='Положить в корзину 😋', callback_data='put into cart')
    ]
    markup.add(*buttons)
    return markup


def back_to_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='⬅ Назад')]
    ], resize_keyboard=True)
