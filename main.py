# coding=utf-8
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from pytz import timezone
from task import get_weathers
from db import db


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('weather_record')
    logger.addHandler(logging.StreamHandler())

    executors = {'default': ThreadPoolExecutor(20)}

    # 确保数据表已经创建
    # 设置定时器，cron任务只需要放内存里。如果需要每隔一定时间执行任务，需要把任务放入数据库
    scheduler = BlockingScheduler(logger=logger, executors=executors, timezone=timezone('Asia/Shanghai'))
    scheduler.add_job(get_weathers, trigger='cron', hour='10')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass