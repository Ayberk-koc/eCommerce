# coding: utf-8
from sqlalchemy import CheckConstraint, Column, DECIMAL, DateTime, Enum, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)


class User(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint('(((`username` is null) and (`password_hash` is null)) or ((`username` is not null) and (`password_hash` is not null)))'),
    )

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    street = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(50), nullable=False)
    is_default = Column(TINYINT(1), server_default=text("'0'"))

    user = relationship('User')


class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship('User')


class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    cart_id = Column(ForeignKey('carts.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)

    cart = relationship('Cart')
    product = relationship('Product')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, index=True)
    status = Column(Enum('pending', 'processing', 'shipped', 'delivered', 'cancelled'), server_default=text("'pending'"))
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    address_id = Column(ForeignKey('addresses.id'), nullable=False, index=True)

    address = relationship('Address')
    user = relationship('User')


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

    order = relationship('Order')
    product = relationship('Product')
