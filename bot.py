from os import path
import os
import nonebot
import config
import logging
from nonebot import logger

if __name__ == '__main__':
    if not path.exists('.' + os.sep + 'asset' + os.sep + 'data' + os.sep):
        os.mkdir('.' + os.sep + 'asset' + os.sep + 'data' + os.sep)
    nonebot.init(config)
    logger.setLevel(logging.DEBUG)
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'asset', 'plugins'),
        'asset.plugins'
    )
    logger.info('Starting')
    nonebot.run()
