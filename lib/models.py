from sqlalchemy import String, Integer, BigInteger, DECIMAL, create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from lib.configs import user, password, ipaddress, db_name
from sqlalchemy.schema import UniqueConstraint

engine = create_engine(f"postgresql://{user}:{password}@{ipaddress}/{db_name}", echo=False)


class Base(DeclarativeBase):
    pass


class Users(Base):
    """База пользователей"""
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    carts: Mapped[int] = relationship('Carts', back_populates="user_cart")
    full_name: Mapped[str] = mapped_column(String(50))
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)

    def __str__(self):
        return f"User(user_id={self.user_id!r}, full_name={self.full_name!r}, " \
               f"telegram_id={self.telegram_id!r},phone={self.phone!r})"

    def __repr__(self):
        return str(self)


class Carts(Base):
    """Временная корзинка покупателя"""
    __tablename__ = "carts"
    cart_id: Mapped[int] = mapped_column(primary_key=True)
    finally_id: Mapped[int] = relationship('Finally_carts', back_populates="user_cart")
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), unique=True)
    user_cart: Mapped[Users] = relationship('Users', back_populates="carts")
    total_price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2), default=0)
    total_products: Mapped[int] = mapped_column(Integer, default=0)

    def __str__(self):
        return f"Cart(cart_id={self.cart_id!r}, " \
               f"user_id={self.user_id!r}, " \
               f"total_price={self.total_price!r}," \
               f"total_products={self.total_products!r})"

    def __repr__(self):
        return str(self)


class Finally_carts(Base):
    """Окончательная корзинка пользователя"""
    __tablename__ = "finally_carts"
    finally_id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey('carts.cart_id'))
    user_cart: Mapped[Carts] = relationship('Carts', back_populates="finally_id")
    product_name: Mapped[str] = mapped_column(String(50))
    quantity: Mapped[int] = mapped_column(Integer)
    final_price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    __table_args__ = (UniqueConstraint('cart_id', 'product_name'),)

    def __str__(self):
        return f"Finally_carts(finally_id={self.finally_id!r}, " \
               f"cart_id={self.cart_id!r}, " \
               f"product_name={self.product_name!r}, " \
               f"quantity={self.quantity!r}, " \
               f"final_price={self.final_price!r})"

    def __repr__(self):
        return str(self)


class Categories(Base):
    """Категории продуктов"""
    __tablename__ = "categories"
    category_id: Mapped[int] = mapped_column(primary_key=True)
    products: Mapped[int] = relationship('Products', back_populates="product_category")
    category_name: Mapped[str] = mapped_column(String(20), unique=True)

    def __str__(self):
        return f"Categories(category_id={self.category_id!r}, " \
               f"category_name={self.category_name!r})"

    def __repr__(self):
        return str(self)


class Products(Base):
    """Продукты"""
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.category_id'))
    product_category: Mapped[Categories] = relationship('Categories', back_populates="products")
    product_name: Mapped[str] = mapped_column(String(20), unique=True)
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    description: Mapped[str] = mapped_column(String(200))
    image: Mapped[str] = mapped_column(String(100))

    def __str__(self):
        return f"Products(product_id={self.product_id!r}, " \
               f"category_id={self.category_id!r}, " \
               f"product_name={self.product_name!r}, " \
               f"price={self.price!r}, " \
               f"description={self.description!r}," \
               f" image={self.image!r})"

    def __repr__(self):
        return str(self)


def main():
    """Только для создания таблиц и первичного наполнения"""
    Base.metadata.create_all(engine)
    categories = ('Лаваши', 'Донары', 'Хот-Доги', 'Десерты', 'Напитки', 'Соусы')
    products = (
        (1, 'Мини лаваш', 20000, 'Мясо, тесто, помидоры', 'media/lavash/lavash_1.jpg'),
        (1, 'Мини говяжий', 22000, 'Мясо, тесто, помидоры', 'media/lavash/lavash_2.jpg'),
        (1, 'Мини с сыром', 24000, 'Мясо, тесто, помидоры', 'media/lavash/lavash_3.jpg')
    )
    with Session(engine) as session:
        for cat in categories:
            query = Categories(category_name=cat)
            session.add(query)
            session.commit()
        for product in products:
            query = Products(
                category_id=product[0],
                product_name=product[1],
                price=product[2],
                description=product[3],
                image=product[4]
            )
            session.add(query)
            session.commit()


if __name__ == '__main__':
    main()
