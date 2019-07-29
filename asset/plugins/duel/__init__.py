import time
import math
import asyncio
import random
from enum import Enum

import nonebot
from nonebot import on_command, CommandSession, permission as perm
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import Message, MessageSegment
from nonebot import logger
from nonebot.typing import Context_T

from .data_source import *
from functions import check_black_list
from functions import tools



__plugin_name__ = '决斗'
__plugin_usage__ = r"""俄罗斯轮盘小游戏，默认六个弹舱1发子弹，输了口随机时间 
(人类为什么不能互相理解啊！！！！)
指令：
！决斗/俄罗斯轮盘 （群成员 可直接命令[空格]+人数）
！自定决斗/自定俄罗斯轮盘 （群成员 可直接命令[空格]+使用的子弹数，子弹用完或者只剩一个人结束）
决斗战绩/查询决斗战绩 (群成员 空格+使用子弹数可查询不同类型的数据，默认查询全部战绩)
！重置决斗/决斗重置 （群管理 重置本群当前决斗）"""

DUEL_DATA = {}
MAX_PART_NUM = 6
TIME_OUT = 40
DEATH_MSG = [
    '果断，就会白给。',
    '犹豫，就会败北。',
    'nickname桑！！nickname桑！！！！这里有医生吗！！我一直，一直对nickname桑你…………哈哈哈哈哈哈哈哈哈嗝',
    '啊，死掉了。',
    '财布-1'
]
MISS_MSG = [
    '欸————竟然没死。',
    '嗯————nickname你真好运',
    '啧！nickname你还活着啊'
]
SHOT_PARTS = [
    '头',
    '胸部',
    '丁丁',
    '小脚趾',
    '最喜欢的手办',
    '暑假作业'
]
MAX_DEATH_MUTE = 600   
MIN_DEATH_MUTE = 60
DEATH_DATA = {}

class duel_state(Enum):
    INIT = 0
    WAIT_OPPONENT = 1
    START_DUEL = 2
    WAIT_CONFIRM = 3
    FINISH = 4

@on_natural_language(keywords={'决斗'})
@check_black_list()
async def duel_nl(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    if '自定决斗' in stripped_msg:
        return
    global DUEL_DATA
    ctx = session.ctx.copy()
    group_id = ctx['group_id']
    if str(group_id) in DUEL_DATA:
        session.send('群里当前已经有人在玩了！')
        return
    num = stripped_msg.replace('决斗', '')
    global MAX_PART_NUM
    if num:
        if tools.is_int(num):
            num = int(num)
            if num < 2 or num > MAX_PART_NUM:
                await session.send('这人数什么鬼？2~6个人啊！你跟那个姓凑学的数学的吗？')
                return
            else:
                return IntentCommand(90.0, 'duel_c', current_arg=num)
        else:
            await session.send('哈？数字！数字懂吗？3x7=27')
            return
    return IntentCommand(90.0, 'duel_c')

@on_command('duel_c', aliases=('决斗', '俄罗斯轮盘'), permission=perm.GROUP_MEMBER)
@check_black_list()
async def duel_c(session: CommandSession):
    global DUEL_DATA
    global TIME_OUT
    global MAX_PART_NUM
    ctx = session.ctx.copy()
    group_id = ctx['group_id']
    user_id = ctx['user_id']
    if str(group_id) in DUEL_DATA:
        session.finish('群里当前已经有人在玩了！')
    part_num = session.get('part_num', prompt='最大参加人数是？')
    if part_num:
        nickname = ''
        if 'card' in ctx['sender']:
            if ctx['sender']['card'] != '':
                nickname = ctx['sender']['card']
            else:
                nickname = ctx['sender']['nickname'] 
        else:
            nickname = ctx['sender']['nickname']
        rand_num = tools.rand_uniint_list(1, MAX_PART_NUM, 1)
        cur_time = math.floor(time.time())
        DUEL_DATA[str(group_id)] = {
            'initiator' : user_id,
            'part_list' : [user_id],
            'max_num': int(part_num),
            'cur_bullet' : rand_num,
            'cur_slot' : 0,
            'state': duel_state.WAIT_OPPONENT,
            'cur_point_user' : 0,
            'bullet_loaded': 1,
            'time': cur_time
        }
        msg = '%s发起俄罗斯轮盘成功！参与者发送含“参上”的信息即可参加！'%nickname
        await session.send(msg)
        asyncio.ensure_future(time_out_check(group_id, cur_time))

@duel_c.args_parser
async def dc_parser(session: CommandSession):
    global MAX_PART_NUM
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg == 'stop':
        session.finish('强制结束手冲')
    if session.is_first_run:
        if stripped_arg and tools.is_int(stripped_arg):
            session.state['part_num'] = int(stripped_arg)
            return
        elif session.current_arg and tools.is_int(session.current_arg):
            session.state['part_num'] = int(session.current_arg)
            return

    elif session.current_key == 'part_num':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not tools.is_int(stripped_arg):
            session.pause('哈？数字！数字懂吗？3x7=27')
        elif int(stripped_arg) < 2 or int(stripped_arg) > MAX_PART_NUM:
            session.pause('这人数什么鬼？2~6个人啊！你跟那个姓凑学的数学的吗？')
        else:
            session.state['part_num'] = int(stripped_arg)

@on_natural_language(keywords={'自定决斗'})
@check_black_list()
async def duel_cus_nl(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    num = stripped_msg.replace('自定决斗', '')
    global MAX_PART_NUM
    global DUEL_DATA
    ctx = session.ctx.copy()
    group_id = ctx['group_id']
    if str(group_id) in DUEL_DATA:
        session.send('群里当前已经有人在玩了！')
        return
    if num:
        if tools.is_int(num):
            num = int(num)
            if num < 1:
                await session.send('你这个子弹数量？你是池沼吗？')
                return
            else:
                return IntentCommand(100.0, 'duel_c_c', current_arg=num)
        else:
            await session.send('哈？数字！数字懂吗？3x7=27')
            return
    return IntentCommand(100.0, 'duel_c_c')

@on_command('duel_c_c', aliases=('自定决斗', '自定俄罗斯轮盘'), permission=perm.GROUP_MEMBER)
@check_black_list()
async def duel_c_c(session: CommandSession):
    global DUEL_DATA
    global TIME_OUT
    global MAX_PART_NUM
    ctx = session.ctx.copy()
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    if str(group_id) in DUEL_DATA:
        session.finish('群里当前已经有人在玩了！')
    max_loaded = session.get('max_loaded', prompt='放进去的子弹数量是？')
    if not max_loaded:
        return
    part_num = session.get('part_num', prompt='最大参加人数是？')
    if not part_num:
        return
    nickname = ''
    if 'card' in ctx['sender']:
        if ctx['sender']['card'] != '':
            nickname = ctx['sender']['card']
        else:
            nickname = ctx['sender']['nickname'] 
    else:
        nickname = ctx['sender']['nickname']
    rand_num = tools.rand_uniint_list(1, MAX_PART_NUM, max_loaded)
    cur_time = math.floor(time.time())
    DUEL_DATA[str(group_id)] = {
        'initiator' : user_id,
        'part_list' : [user_id],
        'max_num': int(part_num),
        'cur_bullet' : rand_num,
        'cur_slot' : 0,
        'state': duel_state.WAIT_OPPONENT,
        'cur_point_user' : 0,
        'bullet_loaded': max_loaded,
        'time': cur_time
    }
    msg = '%s发起俄罗斯轮盘成功！参与者发送含“参上”的信息即可参加！'%nickname
    await session.send(msg)
    asyncio.ensure_future(time_out_check(group_id, cur_time))

@duel_c_c.args_parser
async def dcc_parser(session: CommandSession):
    global MAX_PART_NUM
    ctx = session.ctx.copy()
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg == 'stop':
        session.finish('强制结束手冲')
    if session.is_first_run:
        if stripped_arg and tools.is_int(stripped_arg):
            if int(stripped_arg) > MAX_PART_NUM:
                await session.send('多余的子弹，就送给你吧！')
                await asyncio.sleep(1)
                await session.send('咔嚓')
                await asyncio.sleep(1)
                await session.send('Bang！')
                await asyncio.sleep(1)
                await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=60)
                session.finish('游戏结束！')
                return
            session.state['max_loaded'] = int(stripped_arg)
            return
        elif session.current_arg and tools.is_int(session.current_arg):
            if int(session.current_arg) > MAX_PART_NUM:
                await session.send('多余的子弹，就送给你吧！')
                await asyncio.sleep(1)
                await session.send('咔嚓')
                await asyncio.sleep(1)
                await session.send('Bang！')
                await asyncio.sleep(1)
                await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=60)
                session.finish('游戏结束！')
                return
            session.state['max_loaded'] = int(session.current_arg)
            return

    elif session.current_key == 'max_loaded':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not tools.is_int(stripped_arg):
            session.pause('哈？数字！数字懂吗？3x7=27')
        elif int(stripped_arg) > MAX_PART_NUM:
            await session.send('多余的子弹，就送给你吧！')
            await asyncio.sleep(1)
            await session.send('咔嚓')
            await asyncio.sleep(1)
            await session.send('Bang！')
            await asyncio.sleep(1)
            await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=60)
            session.finish('游戏结束！')
        else:
            session.state['max_loaded'] = int(stripped_arg)

    elif session.current_key == 'part_num':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not tools.is_int(stripped_arg):
            session.pause('哈？数字！数字懂吗？3x7=27')
        elif int(stripped_arg) < 2 or int(stripped_arg) > MAX_PART_NUM:
            session.pause('这人数什么鬼？2~6个人啊！你跟那个姓凑学的数学的吗？')
        else:
            session.state['part_num'] = int(stripped_arg)


async def time_out_check(group_id: int, time: int):
    global bot
    global DUEL_DATA
    await asyncio.sleep(TIME_OUT)
    if not str(group_id) in DUEL_DATA:
        return

    cur_data = DUEL_DATA[str(group_id)]
    data_time = cur_data['time']
    if not data_time == time:
        return
    cur_state = cur_data['state']
    cur_parts = DUEL_DATA[str(group_id)]['part_list']
    if cur_state == duel_state.WAIT_OPPONENT:
        msg = '报名时间到！'
        await bot.send_group_msg(group_id=group_id, message=msg)
        if len(cur_parts) >= 2:
            msg = '俄罗斯转盘开始！咔擦咔擦咔擦~~，参加者有：'
            for s_id in cur_parts:
                s_name = ''
                try:
                    s_info = await bot.get_group_member_info(group_id = group_id, user_id = s_id, no_cache = True)
                    if s_info['card'] != '':
                        s_name = s_info['card']
                    else:
                        s_name = s_info['nickname']
                except:
                    logger.warn('决斗获取个人数据失败')
                if s_name == '':
                    s_name = str(s_id)
                msg = msg + '\n' + s_name
            try:
                await bot.send_group_msg(group_id=group_id, message=msg)
            except:
                pass
            DUEL_DATA[str(group_id)]['state'] = duel_state.START_DUEL
            await duel_manager(group_id)
        else:
            msg = '报名人数不足！'
            await bot.send_group_msg(group_id=group_id, message=msg)
            del DUEL_DATA[str(group_id)]
    elif cur_state == duel_state.WAIT_CONFIRM:
        cur_point_user = cur_data['cur_point_user']
        cur_slot = cur_data['cur_slot']
        cur_bullet = cur_data['cur_bullet']
        bullet_loaded = cur_data['bullet_loaded']
        global DEATH_MSG
        global MISS_MSG
        global MAX_DEATH_MUTE
        global MIN_DEATH_MUTE
        global DEATH_DATA
        cur_slot = cur_slot + 1
        nickname = ''
        try:
            shot_user_info = await bot.get_group_member_info(group_id = group_id, user_id = cur_point_user, no_cache = True)
            if shot_user_info['card'] != '':
                nickname = shot_user_info['card']
            else:
                nickname = shot_user_info['nickname']
        except:
            logger.warn('决斗获取个人数据失败')
        if nickname == '':
            nickname = str(cur_point_user)
        if cur_slot in cur_bullet:
            # cur_parts.remove(cur_point_user)
            cur_bullet.remove(cur_slot)
            msg = '咔嚓!'
            await bot.send_group_msg(group_id=group_id, message=msg)
            await asyncio.sleep(1)
            msg = 'Bang!'
            await bot.send_group_msg(group_id=group_id, message=msg)
            rand_death = random.randint(0, len(DEATH_MSG) - 1)
            msg = DEATH_MSG[rand_death]
            msg = msg.replace('nickname', nickname)
            await bot.set_group_ban(group_id=group_id, user_id=cur_point_user, duration=random.randint(MIN_DEATH_MUTE, MAX_DEATH_MUTE))
            await bot.send_group_msg(group_id=group_id, message=msg)
            # await add_single_duel(cur_point_user, group_id, bullet_loaded, True)
            if not str(group_id) in DEATH_DATA:
                DEATH_DATA[str(group_id)] = []
            DEATH_DATA[str(group_id)].append(cur_point_user)
            if len(cur_bullet) <= 0 or (len(cur_parts) - len(DEATH_DATA[str(group_id)])) <= 1:
                msg = '游戏结束！'
                await bot.send_group_msg(group_id=group_id, message=msg)
                for item in cur_parts:
                    death_list = DEATH_DATA[str(group_id)]
                    if item in death_list:
                        await add_single_duel(item, group_id, bullet_loaded, True)
                    else:
                        await add_single_duel(item, group_id, bullet_loaded, False)
                del DUEL_DATA[str(group_id)]
                del DEATH_DATA[str(group_id)]
                return
            cur_data['state'] = duel_state.START_DUEL
            cur_data['cur_slot'] = cur_slot
            cur_data['cur_bullet'] = cur_bullet
            DUEL_DATA[str(group_id)] = cur_data.copy()
            await duel_manager(group_id)
        else:
            msg = '咔嚓!'
            await bot.send_group_msg(group_id=group_id, message=msg)
            await asyncio.sleep(1)
            rand_miss = random.randint(0, len(MISS_MSG) - 1)
            msg = MISS_MSG[rand_miss]
            msg = msg.replace('nickname', nickname)
            await bot.send_group_msg(group_id=group_id, message=msg)
            # await add_single_duel(cur_point_user, group_id, bullet_loaded, False)
            cur_data['state'] = duel_state.START_DUEL
            cur_data['cur_slot'] = cur_slot
            cur_data['cur_bullet'] = cur_bullet
            DUEL_DATA[str(group_id)] = cur_data.copy()
            await duel_manager(group_id)

bot = nonebot.get_bot()
@bot.on_message('group')
async def handle_group_message(ctx: Context_T):
    raw_message = ctx['raw_message']
    if '参上' in raw_message or '好' in raw_message:
        global DUEL_DATA
        global MAX_PART_NUM
        global bot
        group_id = ctx['group_id']
        user_id = ctx['user_id']
        if str(group_id) in DUEL_DATA:
            cur_data = DUEL_DATA[str(group_id)]
            cur_state = cur_data['state']
            cur_point_user = cur_data['cur_point_user']
            cur_parts = cur_data['part_list']
            max_num = cur_data['max_num']
            nickname = ''
            if 'card' in ctx['sender']:
                if ctx['sender']['card'] != '':
                    nickname = ctx['sender']['card']
                else:
                    nickname = ctx['sender']['nickname'] 
            else:
                nickname = ctx['sender']['nickname']
            if cur_state == duel_state.WAIT_OPPONENT:
                if '参上' in raw_message:
                    if user_id in cur_parts or len(cur_parts) >= max_num:
                        # await bot.send_group_msg(group_id=group_id, message='你已人数已满！')
                        return
                    else:
                        cur_parts.append(user_id)
                        DUEL_DATA[str(group_id)]['part_list'] = cur_parts.copy()
                        msg = '%s参加成功！'%nickname
                        await bot.send_group_msg(group_id=group_id, message=msg)
                        if len(cur_parts) >= max_num:
                            DUEL_DATA[str(group_id)]['state'] = duel_state.START_DUEL
                            msg = '俄罗斯转盘开始！咔擦咔擦咔擦~~，参加者有：'
                            for s_id in cur_parts:
                                s_name = ''
                                try:
                                    s_info = await bot.get_group_member_info(group_id = group_id, user_id = s_id, no_cache = True)
                                    if s_info['card'] != '':
                                        s_name = s_info['card']
                                    else:
                                        s_name = s_info['nickname']
                                except:
                                    logger.warn('决斗获取个人数据失败')
                                if s_name == '':
                                    s_name = str(s_id)
                                msg = msg + '\n' + s_name
                            try:
                                await bot.send_group_msg(group_id=group_id, message=msg)
                            except:
                                pass
                            await duel_manager(group_id)

            elif cur_state == duel_state.WAIT_CONFIRM and '好' in raw_message:
                cur_point_user = cur_data['cur_point_user']
                if not user_id == cur_point_user:
                    return
                DUEL_DATA[str(group_id)]['time'] = 0
                cur_slot = cur_data['cur_slot']
                cur_bullet = cur_data['cur_bullet']
                bullet_loaded = cur_data['bullet_loaded']
                global DEATH_MSG
                global MISS_MSG
                global MAX_DEATH_MUTE
                global MIN_DEATH_MUTE
                global DEATH_DATA
                cur_slot = cur_slot + 1
                nickname = ''
                try:
                    shot_user_info = await bot.get_group_member_info(group_id = group_id, user_id = cur_point_user, no_cache = True)
                    if shot_user_info['card'] != '':
                        nickname = shot_user_info['card']
                    else:
                        nickname = shot_user_info['nickname']
                except:
                    logger.warn('决斗获取个人数据失败')
                if nickname == '':
                    nickname = str(cur_point_user)
                if cur_slot in cur_bullet:
                    # cur_parts.remove(cur_point_user)
                    cur_bullet.remove(cur_slot)
                    msg = '咔嚓!'
                    await bot.send_group_msg(group_id=group_id, message=msg)
                    await asyncio.sleep(1)
                    msg = 'Bang!'
                    await bot.send_group_msg(group_id=group_id, message=msg)
                    rand_death = random.randint(0, len(DEATH_MSG) - 1)
                    msg = DEATH_MSG[rand_death]
                    msg = msg.replace('nickname', nickname)
                    await bot.set_group_ban(group_id=group_id, user_id=cur_point_user, duration=random.randint(MIN_DEATH_MUTE, MAX_DEATH_MUTE))
                    await bot.send_group_msg(group_id=group_id, message=msg)
                    # await add_single_duel(cur_point_user, group_id, bullet_loaded, True)
                    if not str(group_id) in DEATH_DATA:
                        DEATH_DATA[str(group_id)] = []
                    DEATH_DATA[str(group_id)].append(cur_point_user)
                    if len(cur_bullet) <= 0 or (len(cur_parts) - len(DEATH_DATA[str(group_id)])) <= 1:
                        msg = '游戏结束！'
                        await bot.send_group_msg(group_id=group_id, message=msg)
                        for item in cur_parts:
                            death_list = DEATH_DATA[str(group_id)]
                            if item in death_list:
                                await add_single_duel(item, group_id, bullet_loaded, True)
                            else:
                                await add_single_duel(item, group_id, bullet_loaded, False)
                        del DUEL_DATA[str(group_id)]
                        del DEATH_DATA[str(group_id)]
                        return
                    cur_data['state'] = duel_state.START_DUEL
                    cur_data['cur_slot'] = cur_slot
                    cur_data['cur_bullet'] = cur_bullet
                    DUEL_DATA[str(group_id)] = cur_data.copy()
                    await duel_manager(group_id)
                else:
                    msg = '咔嚓!'
                    await bot.send_group_msg(group_id=group_id, message=msg)
                    await asyncio.sleep(1)
                    rand_miss = random.randint(0, len(MISS_MSG) - 1)
                    msg = MISS_MSG[rand_miss]
                    msg = msg.replace('nickname', nickname)
                    await bot.send_group_msg(group_id=group_id, message=msg)
                    # await add_single_duel(cur_point_user, group_id, bullet_loaded, False)
                    cur_data['state'] = duel_state.START_DUEL
                    cur_data['cur_slot'] = cur_slot
                    cur_data['cur_bullet'] = cur_bullet
                    DUEL_DATA[str(group_id)] = cur_data.copy()
                    await duel_manager(group_id)


async def duel_manager(group_id : int):
    global DUEL_DATA
    global MAX_PART_NUM
    global bot
    global SHOT_PARTS
    global DEATH_DATA
    if not str(group_id) in DUEL_DATA:
        return
    cur_data = DUEL_DATA[str(group_id)]
    cur_state = cur_data['state']
    cur_parts = cur_data['part_list']
    cur_point_user = cur_data['cur_point_user']
    cur_death = []
    if not str(group_id) in DEATH_DATA:
        DEATH_DATA[str(group_id)] = []
    cur_death = DEATH_DATA[str(group_id)]
    if cur_state == duel_state.START_DUEL:
        # cur_shot_index = cur_slot % len(cur_parts)
        # cur_parts_copy = cur_parts.copy()
        # for item in cur_death:
        #     cur_parts_copy.remove(item)
        # cur_shot_index = 0
        # if cur_point_user:
        #     cur_index = cur_parts.index(cur_point_user)
        #     if cur_index >= len(cur_parts) - 1:
        #         cur_shot_index = 0
        #     else:
        #         cur_shot_index = cur_index + 1
        # cur_shot_user = cur_parts_copy[cur_shot_index]
        cur_shot_user = 0
        if cur_point_user:
            cur_index = cur_parts.index(cur_point_user)
            next_part = 0
            if cur_index == len(cur_parts) - 1:
                next_part = cur_parts[0]
            else:
                next_part = cur_parts[cur_index + 1]
            while next_part in cur_death:
                temp_index = cur_parts.index(next_part)
                if temp_index == len(cur_parts) - 1:
                    next_part = cur_parts[0]
                else:
                    next_part = cur_parts[temp_index + 1]
            cur_shot_user = next_part
        else:
            cur_shot_user = cur_parts[0]
        nickname = ''
        try:
            shot_user_info = await bot.get_group_member_info(group_id = group_id, user_id = cur_shot_user, no_cache = True)
            if shot_user_info['card'] != '':
                nickname = shot_user_info['card']
            else:
                nickname = shot_user_info['nickname']
        except:
            logger.warn('决斗获取个人数据失败')
        if nickname == '':
            nickname = str(cur_shot_user)
        ran_part_int = random.randint(0, len(SHOT_PARTS) - 1)
        msg = '（用枪抵住%s的%s）做好觉悟的吗？（回含有“好”的句子继续）'%(
            nickname,
            SHOT_PARTS[ran_part_int]
        )
        await bot.send_group_msg(group_id = group_id, message = msg)
        # cur_parts.append(cur_shot_user)
        # cur_data['part_list'] = cur_parts
        cur_data['state'] = duel_state.WAIT_CONFIRM
        cur_data['cur_point_user'] = cur_shot_user
        cur_time = math.floor(time.time())
        cur_data['time'] = cur_time
        DUEL_DATA[str(group_id)] = cur_data.copy()
        asyncio.ensure_future(time_out_check(group_id, cur_time))

@on_command('duel_query_single', aliases=('决斗战绩', '查询决斗战绩'), permission=perm.GROUP_MEMBER)
@check_black_list()
async def duel_query_single(session: CommandSession):
    ctx = session.ctx.copy()
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    bullet_query = session.get('bullet_query',prompt = '查询使用的子弹个数的数据')
    query_data = await get_user_duel_data(group_id, user_id, bullet_query)
    nickname = ''
    if 'card' in ctx['sender']:
        if ctx['sender']['card'] != '':
            nickname = ctx['sender']['card']
        else:
            nickname = ctx['sender']['nickname'] 
    else:
        nickname = ctx['sender']['nickname']
    msg = ''
    if not query_data:
        msg = '%s你个池沼根本没参加过这类型的决斗！'%nickname
    else:
        msg = '%s你当前战绩是：\n存活：%s次\n死亡：%s次'%(
            nickname,
            str(query_data['alive']),
            str(query_data['death'])
            )
    await session.send(msg)


@duel_query_single.args_parser
async def dqs_parser(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg == 'stop':
        session.finish('强制结束手冲')
    if session.is_first_run:
        if stripped_arg and tools.is_int(stripped_arg):
            session.state['bullet_query'] = int(stripped_arg)
            return
        elif session.current_arg and tools.is_int(session.current_arg):
            session.state['bullet_query'] = int(session.current_arg)
            return
        else:
            session.state['bullet_query'] = 0
            return


@on_command('clear_data', aliases=('重置决斗', '决斗重置'), permission=perm.GROUP_ADMIN)
@check_black_list()
async def clear_data(session: CommandSession):
    ctx = session.ctx.copy()
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    global DUEL_DATA
    if str(group_id) in DUEL_DATA:
        del DUEL_DATA[str(group_id)]
        await session.send('成功！')

@on_command('query_duel_data', aliases=('排行决斗', '决斗排行'), permission=perm.GROUP_ADMIN)
@check_black_list()
async def query_duel_data(session: CommandSession):
    ctx = session.ctx.copy()
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    duel_data = await get_user_duel_data(group_id = group_id, bullets_use=1)
    print(duel_data)

check_file()