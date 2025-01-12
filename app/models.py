from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    registration_date = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    phone = relationship('PhoneNumber', back_populates='user', cascade='all, delete-orphan')
    goods = relationship('Goods', back_populates='user', cascade='all, delete-orphan')


class Goods(Base):
    __tablename__ = 'goods'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    url = Column(String, unique=True, nullable=True)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=True)
    views = Column(Integer, nullable=True)
    publication_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    image = relationship('Image', back_populates='goods', cascade='all, delete-orphan')
    category = relationship('Category', back_populates='goods', cascade='all, delete-orphan')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='goods')


class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    goods_id = Column(Integer, ForeignKey('goods.id'), nullable=False)
    goods = relationship('Goods', back_populates='image')


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    goods_id = Column(Integer, ForeignKey('goods.id'), nullable=False)
    goods = relationship('Goods', back_populates='category')


class PhoneNumber(Base):
    __tablename__ = 'phone_numbers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='phone')
