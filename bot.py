from os import path
import os
import nonebot
import config

if __name__ == '__main__':
    if not path.exists('.' + os.sep + 'asset' + os.sep + 'data' + os.sep):
        os.mkdir('.' + os.sep + 'asset' + os.sep + 'data' + os.sep)
    nonebot.init(config)
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'asset', 'plugins'),
        'asset.plugins'
    )
    nonebot.run()
