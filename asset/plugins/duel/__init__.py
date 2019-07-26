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

from functions import check_black_list
from functions import tools



__plugin_name__ = '决斗'
__plugin_usage__ = r"""俄罗斯轮盘小游戏，六个弹舱1发子弹，输了口2小时33分
指令：
决斗/！俄罗斯轮盘 （群成员 可直接命令+人数）"""

DUEL_DATA = {}
MAX_PART_NUM = 6
TIME_OUT = 60
DEATH_MSG = [
    '犹豫，就会败北。',
    'nickname桑！！nickname桑！！！！这里有医生吗！！我一直，一直对nickname桑你…………哈哈哈哈哈哈哈哈哈嗝',
    '啊，死掉了。'
]
MISS_MSG = [
    '欸————竟然没死。',
    'nickname你真好运',
    '啧！nickname你还活着啊'
]
SHOT_PARTS = [
    '头',
    '胸',
    '丁丁',
    '小脚趾',
    '最喜欢的手办'
]
DEATH_MUTE = 153 * 60

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
    num = stripped_msg.replace('决斗', '')
    global MAX_PART_NUM
    if num:
        if tools.is_int(num):
            num = int(num)
            if num < 2 or num > MAX_PART_NUM:
                return IntentCommand(90.0, 'duel_c', current_arg=num)
            else:
                await session.send('这人数什么鬼？2~6个人啊！你跟那个姓凑学的数学的吗？')
        else:
            await session.send('哈？数字！数字懂吗？3x7=27')
    return IntentCommand(90.0, 'duel_c')

@on_command('duel_c', aliases=('决斗', '俄罗斯轮盘'), permission=perm.GROUP_MEMBER)
@check_black_list()
async def duel_c(session: CommandSession):
    global DUEL_DATA
    global TIME_OUT
    global MAX_PART_NUM
    ctx = session.ctx.copy()
    user_id = ctx['user_id']
    group_id = ctx['group_id']
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
        rand_num = random.randint(1, MAX_PART_NUM)
        DUEL_DATA[str(group_id)] = {
            'initiator' : user_id,
            'participants' : [user_id],
            'max_num': int(part_num),
            'cur_bullet' : rand_num,
            'cur_slot' : 0,
            'state': duel_state.WAIT_OPPONENT,
            'cur_point' : 0
        }
        msg = '%s发起俄罗斯轮盘成功！参与者发送含“参上”的信息即可参加！'%nickname
        await session.send(msg)
        asyncio.ensure_future(time_out_check(group_id))

        

async def time_out_check(group_id: int):
    global bot
    global DUEL_DATA
    await asyncio.sleep(TIME_OUT)
    if DUEL_DATA[str(group_id)]['state'] == duel_state.WAIT_OPPONENT:
        msg = '报名时间到！'
        await bot.send_group_msg(group_id=group_id, message=msg)
        cur_parts = DUEL_DATA[str(group_id)]['participants']
        if len(cur_parts) >= 2:
            msg = '俄罗斯转盘开始！咔擦咔擦咔擦~~，参加者有：'
            for s_id in cur_parts:
                s_name = ''
                try:
                    s_info = await bot.get_group_member_info(group_id = group_id, user_id = s_id)
                    if 'card' in s_info:
                        s_name = s_info['card']
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
        else:
            msg = '报名人数不足！'
            await bot.send_group_msg(group_id=group_id, message=msg)
            del DUEL_DATA[str(group_id)]

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

    elif session.current_key == 'part_num':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not tools.is_int(stripped_arg):
            session.pause('哈？数字！数字懂吗？3x7=27')
        elif int(stripped_arg) < 2 or int(stripped_arg) > MAX_PART_NUM:
            session.pause('这人数什么鬼？2~6个人啊！你跟那个姓凑学的数学的吗？')
        else:
            session.state['part_num'] = int(stripped_arg)

bot = nonebot.get_bot()
@bot.on_message('group')
async def handle_group_message(ctx: Context_T):
    raw_message = ctx['raw_message']
    if '参上' in raw_message or '好了' in raw_message:
        global DUEL_DATA
        global MAX_PART_NUM
        global bot
        group_id = ctx['group_id']
        user_id = ctx['user_id']
        if str(group_id) in DUEL_DATA:
            cur_data = DUEL_DATA[str(group_id)]
            cur_state = cur_data['state']
            cur_point = cur_data['cur_point']
            cur_parts = cur_data['participants']
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
                        DUEL_DATA[str(group_id)]['participants'] = cur_parts.copy()
                        msg = '%s参加成功！'%nickname
                        await bot.send_group_msg(group_id=group_id, message=msg)
                        if len(cur_parts) >= max_num:
                            DUEL_DATA[str(group_id)]['state'] = duel_state.START_DUEL
                            msg = '俄罗斯转盘开始！咔擦咔擦咔擦~~，参加者有：'
                            for s_id in cur_parts:
                                s_name = ''
                                try:
                                    s_info = await bot.get_group_member_info(group_id = group_id, user_id = s_id)
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

            elif cur_state == duel_state.WAIT_CONFIRM:
                cur_point_user = cur_point
                cur_slot = cur_data['cur_slot']
                cur_bullet = cur_data['cur_bullet']
                if '好了' in raw_message and user_id == cur_point_user:
                    global DEATH_MSG
                    global MISS_MSG
                    global DEATH_MUTE
                    cur_slot = cur_slot + 1
                    if cur_bullet == cur_slot:
                        rand_death = random.randint(0, len(DEATH_MSG) - 1)
                        msg = DEATH_MSG[rand_death]
                        msg = msg.replace('nickname', nickname)
                        await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=DEATH_MUTE)
                        await bot.send_group_msg(group_id=group_id, message=msg)
                        del DUEL_DATA[str(group_id)]
                        msg = '游戏结束！'
                        await bot.send_group_msg(group_id=group_id, message=msg)
                    else:
                        rand_miss = random.randint(0, len(MISS_MSG) - 1)
                        msg = MISS_MSG[rand_miss]
                        msg = msg.replace('nickname', nickname)
                        await bot.send_group_msg(group_id=group_id, message=msg)
                        cur_data['state'] = duel_state.START_DUEL
                        cur_data['cur_point'] = 0
                        cur_data['cur_slot'] = cur_slot
                        DUEL_DATA[str(group_id)] = cur_data.copy()
                        await duel_manager(group_id)


async def duel_manager(group_id : int):
    global DUEL_DATA
    global MAX_PART_NUM
    global bot
    global SHOT_PARTS
    cur_data = DUEL_DATA[str(group_id)]
    cur_state = cur_data['state']
    cur_parts = cur_data['participants']
    cur_slot = cur_data['cur_slot']
    max_num = cur_data['max_num']
    if not str(group_id) in DUEL_DATA:
        return
    if cur_state == duel_state.START_DUEL:
        cur_shot_index = cur_slot % max_num
        cur_shot_user = cur_parts[cur_shot_index]
        nickname = ''
        try:
            shot_user_info = await bot.get_group_member_info(group_id = group_id, user_id = cur_shot_user)
            if shot_user_info['card'] != '':
                nickname = shot_user_info['card']
            else:
                nickname = shot_user_info['nickname']
        except:
            logger.warn('决斗获取个人数据失败')
        if nickname == '':
            nickname = str(cur_shot_user)
        ran_part_int = random.randint(0, len(SHOT_PARTS) - 1)
        msg = '（用枪抵住%s的%s）做好觉悟的吗？（回含有“好了”的句子继续）'%(
            nickname,
            SHOT_PARTS[ran_part_int]
        )
        await bot.send_group_msg(group_id = group_id, message = msg)
        cur_parts.append(cur_shot_user)
        cur_data['participants'] = cur_parts
        cur_data['state'] = duel_state.WAIT_CONFIRM
        cur_data['cur_point'] = cur_shot_user
        DUEL_DATA[str(group_id)] = cur_data.copy()