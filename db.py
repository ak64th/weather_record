# coding=utf-8
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, DateTime

from config import config

# ###数据库结构

metadata = MetaData()

# 记录外部数据
weather = Table(
    'weather', metadata,
    Column('id', Integer, primary_key=True),
    Column('district', String),
    Column('entry', String),
    Column('format', Integer, default=1),
    Column('timestamp', DateTime, default=datetime.utcnow),
)

db = create_engine(config['DB_URL'], echo=True)

# 程序在创建表格之前会检测是否存在
metadata.create_all(db)
