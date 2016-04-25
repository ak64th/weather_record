# coding=utf-8
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from pytz import timezone
from task import get_weathers
from db import db


if __name__ == '__main__':
    logger = logging.getLogger('weather_record')
    logger.setLevel(logging.DEBUG)
    steam_handler = logging.StreamHandler()
    logger.addHandler(steam_handler)

    jobstores = {'default': SQLAlchemyJobStore(engine=db)}
    executors = {'default': ThreadPoolExecutor(20)}
    job_defaults = {'max_instances': 3}

    # 确保数据表已经创建
    # 设置定时器
    scheduler = BlockingScheduler(logger=logger, jobstores=jobstores, executors=executors, job_defaults=job_defaults,
                                  timezone=timezone('Asia/Shanghai'))
    scheduler.add_job(get_weathers, trigger='cron', hour='10')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass