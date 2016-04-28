# coding=utf-8
import logging
import datetime
import decimal

import requests
from requests.adapters import HTTPAdapter
from config import config
from db import db, actualities, futures


ACTUAL_TIME_FORMAT = '%H:%M'
FUTURE_DATE_FORMAT = '%Y%m%d'

strptime = datetime.datetime.strptime

logger = logging.getLogger('weather_record')


def get_weathers():
    with requests.Session() as s:
        s.mount('http://v.juhe.cn/weather', HTTPAdapter(max_retries=2))
        r = s.get('http://v.juhe.cn/weather/citys',
                  params={'key': config['APP_KEY']},
                  timeout=config['REQUEST_TIMEOUT'])
        data = r.json()

        if 'result' not in data or data['resultcode'] != '200':
            logger.error(u'无法得到区域列表，返回内容:{}'.format(r.text))
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

            if 'result' not in data or data['resultcode'] != '200':
                logger.error(u'无法得到{}地区的天气信息，返回内容:{}'.format(district, resp.text))
                continue

            actuality = data['result']['sk']

            stmt = actualities.insert().values(
                district=district,
                temp=decimal.Decimal(actuality['temp']),
                wind_direction=actuality['wind_direction'],
                wind_strength=actuality['wind_strength'],
                humidity=decimal.Decimal(actuality['humidity'].strip('%')) / 100,
                time=strptime(actuality['time'], ACTUAL_TIME_FORMAT).time()
            )
            connection.execute(stmt)

            future_data = data['result']['future']

            if isinstance(future_data, dict):
                future_data = future_data.values()

            for future in future_data:
                date = strptime(future['date'], FUTURE_DATE_FORMAT).date()
                values = {
                    'district': district,
                    'temperature': future['temperature'],
                    'weather': future['weather'],
                    'weather_id_fa': future['weather_id']['fa'],
                    'weather_id_fb': future['weather_id']['fb'],
                    'wind': future['wind'],
                    'date': date
                }
                restrict = lambda query: query \
                    .where(futures.c.date == date) \
                    .where(futures.c.district == district)
                stmt = restrict(futures.select())
                if connection.execute(stmt).fetchone():
                    stmt = restrict(futures.update().values(**values))
                else:
                    stmt = futures.insert().values(**values)
                connection.execute(stmt)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('weather_record')
    logger.addHandler(logging.StreamHandler())
    get_weathers()