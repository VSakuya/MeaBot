
from nonebot import on_command, CommandSession, permission as perm
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import Message, MessageSegment
from nonebot import logger
import requests
import asyncio
import time
import nonebot
import datetime
import random

from .data_source import *
from functions import special_user
from functions import tools
from functions import check_black_list
from config import global_var
from asset.plugins.mute import remove_all_mute_public

__plugin_name__ = '直播'
__plugin_usage__ = r"""从YTB，B站以及TC台获取直播状态
优先度：B>YTB>TC
指令：
播了吗/直播 (所有人，获取当前直播状态)
救救孩子/请求口球解除 （所有人，可私聊，在直播时可解除口球）"""
LIVE_STARTED = False
ALERT_STARTED = False
ALERT_DATA = {}
example = {1111111:{'count': 0, 'stop': False}}
ALERT_LIMIT = 100
ALERT_LIST = []

@on_natural_language(keywords={'播了吗', '直播'})
@check_black_list()
async def live_status(session: NLPSession):
    ctx = session.ctx.copy()
    bot = session.bot
    global LIVE_STARTED
    if LIVE_STARTED:
        await bot.send(ctx, Message('你醒啦，mea正在播'))
            # await bot.send(ctx, MessageSegment(type_='at', data={'qq': 'all'}) + '\n' + Message('没在播\n'+ json_data['url'] + json_data['title']) + MessageSegment.image(json_data['cover']))
    else:
        await bot.send(ctx, Message('mea还在准备播'))
            # await bot.send(ctx, MessageSegment(type_='at', data={'qq': 'all'}) + '\n' + Message('没在播\n'+ json_data['url'] + json_data['title']) + MessageSegment.image(json_data['cover']))

@on_natural_language(keywords={'救救孩子', '请求口球解除'})
@check_black_list()
async def save_when_live(session: NLPSession):
    global LIVE_STARTED
    if LIVE_STARTED:
        ctx = session.ctx.copy()
        user_id = ctx['user_id']
        bot = session.bot
        group_list = await bot.get_group_list()
        for item in group_list:
            await bot.set_group_ban(group_id = item['group_id'], user_id = user_id, duration = 0)
        await session.send('那这次就放过你吧！')
    else:
        await session.send('Mea还在摸，不给解除~~')

@on_command('live_simulate', aliases = ('模拟开播', '开播模拟'), permission=perm.SUPERUSER)
async def live_simulate(session: CommandSession):
    global LIVE_STARTED
    LIVE_STARTED = True


# @nonebot.scheduler.scheduled_job('interval', seconds=60, id = 'check_live', jitter = 10)
async def check_live():
    bot = nonebot.get_bot()
    local_data_dict = await get_live_data()
    json_data_B = await get_B_live_data()
    json_data_YTB = await get_YB_live_data()
    json_data_TC = await get_TC_live_data()
    is_started_B_live = False
    is_started_YB_live = False
    is_started_TC_live = False
    global LIVE_STARTED
    IntentCommand(90, 'all_mute_disable')
    if not 'live_state' in local_data_dict:
        local_data_dict = {'live_state': True, 'live_time': 0}

    if(json_data_B):
        if int(json_data_B['liveStatus']) == 1:
            is_started_B_live = True
        logger.info('B no live')
    else:
        logger.warn('自动获取B站直播数据出错')

    if json_data_YTB:
        is_started_YB_live = True
    else:
        logger.info('YTB no live')

    if json_data_TC:
        is_started_TC_live = True
    else:
        logger.info('TC no live')

    if (is_started_B_live or is_started_YB_live or is_started_TC_live) and not local_data_dict['live_state']:
        LIVE_STARTED = True
        new_local = {'live_state': True, 'live_time': time.time()}
        await write_live_data(new_local)
        group_list = await bot.get_group_list()
        if is_started_B_live:
            for item in group_list:
                try:
                    await bot.send_group_msg(group_id=item['group_id'], message=MessageSegment(type_='at', data={'qq': 'all'}))
                except:
                    pass
                await bot.send_group_msg(group_id=item['group_id'], message=MessageSegment.share(url=json_data_B['url'], title=json_data_B['title'], content='mea开播啦', image_url=json_data_B['cover']))
        elif not is_started_B_live and is_started_YB_live:
            for item in group_list:
                try:
                    await bot.send_group_msg(group_id=item['group_id'], message=MessageSegment(type_='at', data={'qq': 'all'}))
                except:
                    pass
                await bot.send_group_msg(group_id=item['group_id'], message='Mea正在Youtube直播！！！')
        elif not (is_started_B_live or is_started_YB_live) and is_started_TC_live:
                try:
                    await bot.send_group_msg(group_id=item['group_id'], message=MessageSegment(type_='at', data={'qq': 'all'}))
                except:
                    pass
                await bot.send_group_msg(group_id=item['group_id'], message=MessageSegment.share(url=json_data_TC['url'], title='Mea在TC台直播！', content='mea开播啦', image_url=json_data_TC['image']))
        global ALERT_LIST
        ALERT_LIST = await special_user.get_live_alert_list()
        # for item in group_list:
        #     await remove_all_mute_public(item['group_id'])
    elif not (is_started_B_live or is_started_YB_live or is_started_TC_live) and local_data_dict['live_state']:
        LIVE_STARTED = False
        global ALERT_DATA
        ALERT_DATA = {}
        group_list = await bot.get_group_list()
        for item in group_list:
            await bot.send_group_msg(group_id=item['group_id'], message='直播结束啦！')
        new_local = {'live_state': False, 'live_time': time.time()}
        await write_live_data(new_local)
            # else:
            #     await bot.send_group_msg(ctx, MessageSegment.share(url=json_data['url'], title=json_data['title'], content='mea开播啦', image_url=json_data['cover']))
            #     # await bot.send(ctx, MessageSegment(type_='at', data={'qq': 'all'}) + '\n' + Message('没在播\n'+ json_data['url'] + json_data['title']) + MessageSegment.image(json_data['cover']))
    elif is_started_B_live or is_started_YB_live or is_started_TC_live : 
        LIVE_STARTED = True
    # await bot.send_group_msg(group_id=204421130, message=MessageSegment.share(url=json_data['url'], title=json_data['title'], content='mea开播啦', image_url=json_data['cover']))
    # await bot.send_group_msg(group_id=204421130, message='test')

# @nonebot.scheduler.scheduled_job('interval', id = 'alert_qq', seconds=11)
async def alert_qq():
    global LIVE_STARTED

    if LIVE_STARTED:
        bot = nonebot.get_bot()
        global ALERT_DATA
        global ALERT_LIMIT
        global ALERT_LIST
        if not ALERT_DATA:
            if not ALERT_LIST:
                ALERT_LIST = await special_user.get_live_alert_list()
            for key in ALERT_LIST:
                ALERT_DATA[int(key)] = {'count': 0, 'stop': False}
        
        alert_msg_list = ['直播啦！', '快醒醒！', '起床啦！', '动一下！debu！', '快出来看直播！']

        del_list = []
        for key in ALERT_DATA:
            qq = key
            count = ALERT_DATA[qq]['count']
            stop = ALERT_DATA[qq]['stop']
            if int(count) <= ALERT_LIMIT and not stop:
                index = random.randint(0, len(alert_msg_list) - 1)
                send_status = True
                try:
                    await bot.send_private_msg(user_id=qq, message=alert_msg_list[index] + '（回复‘停下’停下提醒）')
                    ALERT_DATA[qq]['count'] = count + 1
                except:
                    send_status = False
                if not send_status:
                    del_list.append(qq)
        for item in del_list:
            del ALERT_DATA[item]

example = {'live_state': True, 'live_time': 23123121}


@on_natural_language(keywords={'停下'})
async def sing_nl(session: NLPSession):
    ctx = session.ctx.copy()
    global ALERT_DATA
    if ctx['user_id'] in ALERT_DATA:
        count = ALERT_DATA[ctx['user_id']]['count']
        ALERT_DATA[ctx['user_id']] = {'count': count, 'stop': True}
        await session.send('叫了你%d声才回！太菜了！'%count)

check_file()