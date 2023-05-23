from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup

from lib.db_utils import db_get_categories, db_get_products


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


def generate_category_menu() -> InlineKeyboardMarkup:
    # TODO Получить общею сумму с корзинки
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(
            text=f'Ваша корзинка  (TODO сум)',
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
    return markup





