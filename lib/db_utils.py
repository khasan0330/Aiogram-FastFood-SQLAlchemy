from lib.models import *
from typing import Iterable
from sqlalchemy.orm import Session
from sqlalchemy import update
from sqlalchemy.sql.functions import sum

with Session(engine) as session:
    db_session = session


def db_check_user(chat_id: int) -> Users | None:
    query = select(Users).where(Users.telegram_id == chat_id)
    result: Users | None = db_session.scalar(query)
    return result


def db_register_user(full_name: str, chat_id: int) -> None:
    query = Users(full_name=full_name, telegram_id=chat_id)
    db_session.add(query)
    db_session.commit()


def db_update_user(chat_id: int, phone: str) -> None:
    query = update(Users).where(Users.telegram_id == chat_id).values(phone=phone)
    db_session.execute(query)
    db_session.commit()


def db_create_user_cart(chat_id: int) -> None:
    subquery = db_session.scalar(select(Users).where(Users.telegram_id == chat_id))
    query = Carts(user_id=subquery.user_id)
    db_session.add(query)
    db_session.commit()


def db_get_categories() -> Iterable:
    query = select(Categories)
    return db_session.scalars(query)


def db_get_products(category_id: int) -> Iterable:
    query = select(Products).where(Products.category_id == category_id)
    return db_session.scalars(query)


def db_get_product(product_id: int) -> Products:
    query = select(Products).where(Products.product_id == product_id)
    return db_session.scalar(query)


def db_get_user_cart(chat_id: int) -> Carts:
    query = select(Carts).join(Users).where(Users.telegram_id == chat_id)
    return db_session.scalar(query)


def db_get_product_by_name(product_name: str) -> Products:
    query = select(Products).where(Products.product_name == product_name)
    return db_session.scalar(query)


def db_update_to_cart(price: DECIMAL, quantity: int, cart_id: int) -> None:
    quantity = 1 if quantity < 1 else quantity
    total_price = price * quantity
    query = update(Carts).where(
        Carts.cart_id == cart_id
    ).values(
        total_price=total_price,
        total_products=quantity
    )
    db_session.execute(query)
    db_session.commit()


def db_get_final_price(chat_id: int) -> DECIMAL:
    query = select(
        sum(Finally_carts.final_price)
    ).join(Carts).join(Users).where(Users.telegram_id == chat_id)
    return db_session.scalar(query)


def db_ins_or_upd_finally_cart(cart_id, product_name, total_products, total_price):
    try:
        query = Finally_carts(cart_id=cart_id, product_name=product_name, quantity=total_products, final_price=total_price)
        db_session.add(query)
        db_session.commit()
        return True
    except:
        query = update(Finally_carts).where(Finally_carts.product_name == product_name and Finally_carts.cart_id == cart_id).values(quantity=total_products, final_price=total_price)
        db_session.execute(query)
        db_session.commit()
        return False
