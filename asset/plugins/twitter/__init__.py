
from nonebot import on_command, CommandSession, permission as perm
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import Message, MessageSegment
import nonebot

from .data_source import *
from functions import check_black_list


__plugin_name__ = '推特'
__plugin_usage__ = r"""获取并提醒Mea的推特状态
指令：
最新推文 （所有人）"""

@on_natural_language(keywords={'最新推文'})
@check_black_list()
async def lastest_tweet(session: NLPSession):
    ctx = session.ctx.copy()
    bot = session.bot
    tw_data = await pull_twitter_data()
    del ctx['message']
    i = 0
    for key in tw_data:
        msg = Message(tw_data[key]['text'])
        # print(tw_data[key])
        if 'image' in tw_data[key]:
            tw_pic_list = tw_data[key]['image']
            for pic_item in tw_pic_list:
                msg = msg + MessageSegment.image(pic_item)
        if i == 0:
            await bot.send_msg(**ctx, message=msg)
        i = i+1
    i = 0
    
@nonebot.scheduler.scheduled_job('interval', seconds=53)
async def query_timer():
    bot = nonebot.get_bot()
    tw_data = await pull_twitter_data()
    if not tw_data:
        print('No Twitter Data Online!')
        return False
    tw_local_data = await get_twitter_data()
    # new_twitter_keys = []
    print('check twitter')
    for key_latest in tw_data:
        time_latest = int(key_latest)
        time_local = 0
        for key_local in tw_local_data:
            temp_time_local = int(key_local)
            if temp_time_local > time_local:
                time_local = temp_time_local
        if time_latest > time_local:
            print('send new twitter: ' + str(time_latest))
            msg = Message(tw_data[key_latest]['text'])
            try:
                if 'image' in tw_data[key_latest]:
                    tw_pic_list = tw_data[key_latest]['image']
                    for pic_item in tw_pic_list:
                        msg = msg + MessageSegment.image(pic_item)
            except:
                pass
            group_list = await bot.get_group_list()
            for item in group_list:
                await bot.send_group_msg(group_id=item['group_id'], message=msg)
    
    await write_twitter_data(tw_data)

        # if key_latest in tw_local_data :
        #     msg = Message(key_latest + '\n') + Message(tw_data[key_latest]['text'])
        #     if 'image' in tw_data[key_latest]:
        #         tw_pic_list = tw_data[key_latest]['image']
        #         for pic_item in tw_pic_list:
        #             msg = msg + MessageSegment.image(pic_item)
        #     await bot.send_private_msg(user_id=904853953, message=msg)
        #     await write_twitter_data(tw_data)

check_file()

# LIVE_STARTED = False
# ALERT_STARTED = False
# ALERT_DATA = {}
# example = {1111111:{'count': 0, 'stop': False}}
# ALERT_LIMIT = 100
# ALERT_LIST = []

# @on_command('live_status', aliases = ('播了吗', '直播'))
# async def live_status(session: CommandSession):
#     ctx = session.ctx.copy()
#     bot = session.bot
#     json_data = await get_B_live_data()
#     if json_data:
#         if json_data['liveStatus'] == 1:
#             await bot.send(ctx, MessageSegment.share(url=json_data['url'], title=json_data['title'], content='mea开播啦', image_url=json_data['cover']))
#             # await bot.send(ctx, MessageSegment(type_='at', data={'qq': 'all'}) + '\n' + Message('没在播\n'+ json_data['url'] + json_data['title']) + MessageSegment.image(json_data['cover']))
#         else:
#             await bot.send(ctx, MessageSegment.share(url=json_data['url'], title=json_data['title'], content='mea开播啦', image_url=json_data['cover']))
#             # await bot.send(ctx, MessageSegment(type_='at', data={'qq': 'all'}) + '\n' + Message('没在播\n'+ json_data['url'] + json_data['title']) + MessageSegment.image(json_data['cover']))

# @on_command('add_live_alert_user', aliases = ('添加开播通知名单', '开播通知名单添加'))
# async def add_live_alert_user(session: CommandSession):
#     member_list = await get_live_alert_list_data()
#     new_member = session.get('new_member', prompt='被大吵大闹新成员的Q号？')
#     if new_member in member_list:
#         session.finish('Ta已经在名单里了！')
#     else:
#         member_list.append(new_member)
#         result = await write_live_alert_list_data(member_list)
#         if result:
#             session.finish('搞定，快夸我！')
#         else:
#             session.finish('发生错误啦！')

# @add_live_alert_user.args_parser
# async def alau_parser(session: CommandSession):
#     stripped_arg = session.current_arg_text.strip()
#     if stripped_arg == 'stop':
#         session.finish('强制结束手冲')
#     if session.current_key == 'new_member':
#         if not stripped_arg:
#             session.pause('你哑巴了嘛')
#         if not is_int(stripped_arg):
#             session.pause('哈？你觉得这个像Q号吗？')
#         session.state['new_member'] = int(stripped_arg)

# @on_command('live_simulate', aliases = ('模拟开播', '开播模拟'))
# async def live_simulate(session: CommandSession):
#     global LIVE_STARTED
#     LIVE_STARTED = True


# @nonebot.scheduler.scheduled_job('interval', minutes=1)
# async def query_timer():
#     bot = nonebot.get_bot()
#     local_data_dict = await get_live_data()
#     json_data = await get_B_live_data()
    
#     if not 'live_state' in local_data_dict:
#         local_data_dict = {'live_state': True, 'live_time': 0}
#     if(json_data):
#         global LIVE_STARTED
#         if json_data['liveStatus'] == 1 and not local_data_dict['live_state']:
#             LIVE_STARTED = True
#             group_list = await bot.get_group_list()
#             for item in group_list:
#                 await bot.send_group_msg(group_id=item['group_id'], message=MessageSegment(type_='at', data={'qq': 'all'}))
#                 await bot.send_group_msg(group_id=item['group_id'], message=MessageSegment.share(url=json_data['url'], title=json_data['title'], content='mea开播啦', image_url=json_data['cover']))
            
#             new_local = {'live_state': True, 'live_time': time.time()}
#             await write_live_data(new_local)

#         elif json_data['liveStatus'] == 0 and local_data_dict['live_state']:
#             LIVE_STARTED = False
#             global ALERT_DATA
#             ALERT_DATA = None
#             group_list = await bot.get_group_list()
#             for item in group_list:
#                 await bot.send_group_msg(group_id=item['group_id'], message='直播结束啦！')
#             new_local = {'live_state': False, 'live_time': time.time()}
#             await write_live_data(new_local)

#     else:
#         bot.send_private_msg(user_id = 904853953, message='自动获取B站直播数据出错')
#             # else:
#             #     await bot.send_group_msg(ctx, MessageSegment.share(url=json_data['url'], title=json_data['title'], content='mea开播啦', image_url=json_data['cover']))
#             #     # await bot.send(ctx, MessageSegment(type_='at', data={'qq': 'all'}) + '\n' + Message('没在播\n'+ json_data['url'] + json_data['title']) + MessageSegment.image(json_data['cover']))

#     # await bot.send_group_msg(group_id=204421130, message=MessageSegment.share(url=json_data['url'], title=json_data['title'], content='mea开播啦', image_url=json_data['cover']))
#     # await bot.send_group_msg(group_id=204421130, message='test')

# @nonebot.scheduler.scheduled_job('interval', seconds=5)
# async def alert_qq():
#     global LIVE_STARTED
#     if(LIVE_STARTED):
#         global ALERT_DATA
#         global ALERT_LIMIT
#         global ALERT_LIST
#         bot = nonebot.get_bot()
#         if not ALERT_DATA:
#             if not ALERT_LIST:
#                 ALERT_LIST = await get_live_alert_list_data()
#             for item in ALERT_LIST:
#                 ALERT_DATA[item] = {'count': 0, 'stop': False}
        
#         alert_msg_list = ['直播啦！', '快醒醒！', '起床啦！', '动一下！debu！', '快出来看直播！']

#         for key in ALERT_DATA:
#             qq = key
#             count = ALERT_DATA[qq]['count']
#             stop = ALERT_DATA[qq]['stop']
#             if count <= ALERT_LIMIT and not stop:
#                 index = random.randint(0, len(alert_msg_list) - 1)
#                 await bot.send_private_msg(user_id=qq, message=alert_msg_list[index] + '（回复‘停下’停下提醒）')
#                 ALERT_DATA[qq]['count'] = count + 1

# example = {'live_state': True, 'live_time': 23123121}
