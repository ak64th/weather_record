# coding=utf-8
import logging

import requests
from config import config
from db import db, weather


logger = logging.getLogger('weather_record')


def get_and_save_district_weather(district):
    r = requests.get('http://v.juhe.cn/weather/index', params={
        'cityname': district, 'key': config['APP_KEY'], 'format': 1
    })
    data = r.json()
    logger.debug(r.text)
    logger.debug(data.get('resultcode') + u' - ' + data.get('reason'))

    if 'result' not in data:
        logger.error(u'无法得到{}地区的天气信息'.format(district))
        return

    sql = weather.insert().values(
        district=district,
        entry=r.text,
        format=1,
    )
    with db.connect() as connection:
        result = connection.execute(sql)
    return result.inserted_primary_key


def get_weathers():
    r = requests.get('http://v.juhe.cn/weather/citys', params={'key': config['APP_KEY']})
    data = r.json()
    logger.debug(r.text)
    logger.debug(data.get('resultcode') + u' - ' + data.get('reason'))
    if 'result' not in data:
        logger.error(u'无法得到区域列表')
        return
    districts = [row.get('district') for row in data['result'] if row.get('city') in config['REQUEST_CITIES']]

    for district in districts:
        get_and_save_district_weather(district)
