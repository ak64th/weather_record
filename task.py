# coding=utf-8
import logging

import requests
from config import config
from db import db, weather
from requests.adapters import HTTPAdapter


logger = logging.getLogger('weather_record')


def get_weathers():
    with requests.Session() as s:
        s.mount('http://v.juhe.cn/weather', HTTPAdapter(max_retries=3))
        r = s.get('http://v.juhe.cn/weather/citys',
                  params={'key': config['APP_KEY']},
                  timeout=config['REQUEST_TIMEOUT'])
        data = r.json()

        if 'result' not in data:
            logger.error(u'无法得到区域列表')
            return

        districts = [row.get('district') for row in data['result']
                     if row.get('city') in config['REQUEST_CITIES']]

        resps = [s.get('http://v.juhe.cn/weather/index',
                       params={'cityname': district, 'key': config['APP_KEY'], 'format': 1},
                       timeout=config['REQUEST_TIMEOUT'])
                 for district in districts]

    with db.connect() as connection:
        for resp, district in zip(resps, districts):
            data = resp.json()

            if 'result' not in data:
                logger.error(u'无法得到{}地区的天气信息'.format(district))
                continue

            sql = weather.insert().values(
                district=district,
                entry=resp.text,
                format=1,
            )
            connection.execute(sql)

if __name__ == '__main__':
    logger = logging.getLogger('weather_record')
    logger.setLevel(logging.DEBUG)
    steam_handler = logging.StreamHandler()
    logger.addHandler(steam_handler)
    get_weathers()