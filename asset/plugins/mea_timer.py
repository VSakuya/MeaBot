import os
import asyncio
import nonebot
import pytz
import random
import asyncio
import config
import zipfile
from nonebot import logger
from datetime import datetime

import asset.plugins.live as live
import asset.plugins.twitter as twitter
import asset.plugins.mute as mute
import asset.plugins.leisure_talk as l_talk

RAND_COUNT = 0

@nonebot.scheduler.scheduled_job('cron', id = 'main_timer', second='*/5')
async def main_timer():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    global RAND_COUNT
    asyncio.ensure_future(live.alert_qq())
    # asyncio.ensure_future(l_talk.check_is_leisure())
    if now.second == 0:
        RAND_COUNT = random.randint(0, 3)
    if now.second == RAND_COUNT * 5:
        asyncio.ensure_future(live.check_live())
        asyncio.ensure_future(twitter.check_twitter())
        pass
    if now.hour == 0 and now.minute <= 30 and now.second == 0:
        asyncio.ensure_future(daily_del_file())
        await mute.daily_update(now.year, now.month, now.day, now.hour, datetime.isoweekday(now))
    if now.minute == 0:
        asyncio.ensure_future(check_online())
        asyncio.ensure_future(backup_data())

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

bot = nonebot.get_bot()
async def check_online():
    global bot
    status = await bot.get_status()
    alert_msg = ''
    if not status['online']:
        alert_msg += '登陆状态异常！'
    if alert_msg == '':
        return
    sus = config.global_var.get_super_users()
    for su in sus:
        await bot.send_private_msg(user_id = su, message = alert_msg)

async def backup_data():
    logger.info('开始备份json文件')
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    filename = ''
    filename = filename + str(now.year) + '_' + str(now.month) + '_' + str(now.day) + '_' + str(now.hour) + '.zip'
    backup_dest = os.path.join(os.path.curdir, 'asset', 'backup')
    filename = os.path.join(backup_dest, filename)
    if not os.path.exists(backup_dest):
        os.mkdir(backup_dest)
    zfile = zipfile.ZipFile(filename, 'w')
    backup_dir = os.path.join(os.path.curdir, 'asset', 'data')
    for f_name in os.listdir(backup_dir):
        if 'json' in f_name:
            filepath = os.path.join(backup_dir, f_name)
            zfile.write(filepath, filepath[len(backup_dir):])
    zfile.close()