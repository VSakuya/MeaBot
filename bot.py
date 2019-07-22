from os import path
import os
import nonebot
import config
import logging
from nonebot import logger

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
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'asset', 'plugins'),
        'asset.plugins'
    )
    logger.info('Starting')
    nonebot.run()
