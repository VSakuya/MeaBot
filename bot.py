from os import path
import os
import nonebot
import config
import logging
import math
import time
from nonebot.log import logger

def check_file():
    n_dirs = config.global_var.get_necessary_dir()
    for n_dir in n_dirs:
        if not os.path.exists(n_dir):
            os.mkdir(n_dir)
    logger.info('Dirs checked')

if __name__ == '__main__':
    if not path.exists(path.join(path.dirname(__file__), 'asset', 'data')):
        os.mkdir(path.join(path.dirname(__file__), 'asset', 'data'))
    check_file()
    nonebot.init(config)
    logger.setLevel(logging.DEBUG)
    log_filename = str(math.floor(time.time())) + '.log'
    log_dir = path.join(path.dirname(__file__), 'log', log_filename)
    logging.basicConfig(filename = log_dir)
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'asset', 'plugins'),
        'asset.plugins'
    )
    logger.info('Starting')
    nonebot.run()
