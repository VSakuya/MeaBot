from os import path
import os
import nonebot
import config
import logging
import math
import time
from pytz import timezone, utc
from datetime import datetime
from nonebot.log import logger

def check_file():
    n_dirs = config.global_var.get_necessary_dir()
    for n_dir in n_dirs:
        if not os.path.exists(n_dir):
            os.mkdir(n_dir)
    logger.info('Dirs checked')

def customTime(*args):
    utc_dt = utc.localize(datetime.utcnow())
    my_tz = timezone("Asia/Shanghai")
    converted = utc_dt.astimezone(my_tz)
    return converted.timetuple()

if __name__ == '__main__':
    if not path.exists(path.join(path.dirname(__file__), 'asset', 'data')):
        os.mkdir(path.join(path.dirname(__file__), 'asset', 'data'))
    check_file()
    nonebot.init(config)
    logger.setLevel(logging.DEBUG)
    log_filename = str(math.floor(time.time())) + '.log'
    log_dir = path.join(path.dirname(__file__), 'log', log_filename)
    logging.basicConfig(
        filename = log_dir, 
        format = '%(asctime)s-%(name)s-%(funcName)s-%(levelname)s-%(message)s'
    )
    logging.Formatter.converter = customTime
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'asset', 'plugins'),
        'asset.plugins'
    )
    logger.info('Starting')
    nonebot.run()
