import os
import asyncio
import nonebot
import pytz
import random
import asyncio
import config
from nonebot import logger
from datetime import datetime

import asset.plugins.live as live
import asset.plugins.twitter as twitter
import asset.plugins.mute as mute

RAND_COUNT = 0

@nonebot.scheduler.scheduled_job('cron', id = 'main_timer', second='*/5')
async def main_timer():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    global RAND_COUNT
    if now.second == 0:
        RAND_COUNT = random.randint(0, 3)
    if now.second == RAND_COUNT * 5:
        asyncio.ensure_future(live.check_live())
        asyncio.ensure_future(twitter.check_twitter())
    asyncio.ensure_future(live.alert_qq())
    if now.hour == 0 and now.minute <= 10 and now.second == 0:
        asyncio.ensure_future(daily_del_file())
        await mute.daily_update(now.year, now.month, now.day, now.hour, datetime.isoweekday(now))

async def daily_del_file():
    dirs_list = [
        os.path.join(config.global_var.get_coolq_dir(), 'data', 'record'),
        os.path.join(config.global_var.get_coolq_dir(), 'data', 'image')
    ]

    for single_dir in dirs_list:
        file_list = os.listdir(single_dir)
        for item in file_list:
            file_dir = os.path.join(single_dir, item)
            if not os.path.isdir(file_dir):
                os.remove(file_dir)