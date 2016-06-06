# coding=utf-8
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, DateTime, Date, Time, Numeric

from config import config

# ###数据库结构

metadata = MetaData()

# 记录天气实况数据
actualities = Table(
    'actualities', metadata,
    Column('id', Integer, primary_key=True),
    Column('district', String(255)),
    Column('temp', Numeric(precision=1)),
    Column('wind_direction', String(255)),
    Column('wind_strength', String(255)),
    Column('humidity', Numeric(precision=2)),
    Column('time', Time),
    Column('created_at', DateTime, default=datetime.utcnow),
)

# 记录七天内天气预报数据，每日更新
futures = Table(
    'futures', metadata,
    Column('id', Integer, primary_key=True),
    Column('district', String(255)),
    Column('temperature', String(255)),
    Column('weather', String(255)),
    Column('weather_id_fa', String(255)),
    Column('weather_id_fb', String(255)),
    Column('wind', String(255)),
    Column('date', Date, index=True),
    Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)

db = create_engine(config['DB_URL'], echo=True)


# 程序在创建表格之前会检测是否存在
metadata.create_all(db)
