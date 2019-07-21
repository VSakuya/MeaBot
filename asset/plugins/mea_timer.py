import asyncio
import nonebot
import pytz
import random
import asyncio
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
        await mute.daily_update(now.year, now.month, now.day, now.hour, datetime.isoweekday(now))

