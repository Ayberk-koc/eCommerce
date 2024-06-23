# coding: utf-8
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class InitialTable(Base):
    __tablename__ = 'initial_table'

    id = Column(Integer, primary_key=True)
