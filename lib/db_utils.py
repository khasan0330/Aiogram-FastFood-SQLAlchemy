from lib.models import *
from typing import Iterable
from sqlalchemy.orm import Session
from sqlalchemy import update

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
