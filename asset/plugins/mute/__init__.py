import asyncio
import nonebot
import random
import math
import pytz
import traceback
from nonebot.typing import Context_T
from nonebot import on_command, CommandSession, permission as perm
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import Message, MessageSegment
from nonebot import logger

from datetime import datetime
from aiocqhttp.exceptions import Error as CQHttpError
from .data_source import *
from functions import tools
from functions import check_black_list
from config import global_var


__plugin_name__ = '迫害插件'
__plugin_usage__ = """根据关键字禁言（需管理员权限）
指令：
！整理迫害/迫害整理 （bot管理员）

！添加迫害/迫害添加 （群管理员）

！迫害列表/列表迫害 （群管理员）

！删除迫害/迫害删除 （群管理员）

！代抽口球/口球代抽 (群管理员 +命令+群昵称（可不完整）或完整qq号) 

口球 （任何人 普通包含：上限30分钟；包含“睡眠”：上限8小时;包含“大”字：上限1天；包含“终极”：上限30天，请在管理员陪同下尝试）

！当前豁免几率/当前赦免概率 (群成员)

献祭自己/我来做祭品 （任何人 献祭一个小时来换取mea直播机会）

！大赦天下/全部解除口球 （群管理员，昵称带有“考试”，“备考”，“高考”，“ks”的群友不会被解除）

！口球统计/统计口球 （任何人 一些没什么卵用的信息）

！救救帕里 （bot管理员 救救被测试时工伤了的bot帕里"""

DATA_LIST = None

REMOVE_IGNORE_LIST = ['考试', '备考', '高考', 'ks']


@on_command('save_paryi', aliases = ('救救帕里', 'bot管理员拯救'), permission=perm.SUPERUSER)
async def save_paryi(session: CommandSession):
    bot = session.bot
    g_list = []
    try:
        g_list = await bot.get_group_list()
    except:
        logger.warn('获取群数据错误！')
    for item in g_list:
        await bot.set_group_ban(group_id=item['group_id'], user_id=904853953, duration=0)

@on_command('mute_arrange', aliases = ('整理迫害', '迫害整理'), permission=perm.SUPERUSER)
async def mute_arrange(session: CommandSession):
    await arrange_data()
    await session.send('整理完毕')

@on_command('mute_list', aliases = ('迫害列表', '列表迫害'), permission=perm.GROUP_ADMIN)
@check_black_list()
async def mute_list(session: CommandSession):
    global DATA_LIST
    group_id = session.ctx['group_id']
    DATA_LIST = await get_mute_data()
    if not DATA_LIST:
        await session.send('列表为空！')
    else:
        data_str = ''
        for i in range(len(DATA_LIST)):
            item = DATA_LIST[i]
            if group_id == item['group_id']:
                data_str = data_str + '\n' + str(i+1) + '. ' + 'QQ:' +str(item['user_id']) + ' 群:' + str(item['group_id']) + ' 关键字:' + str(item['key_word']) + ' 时长:' + str([item['mute_time']])
        await session.send(data_str)

@on_command('mute_del_by_index', aliases = ('删除迫害', '迫害删除'), permission=perm.GROUP_ADMIN)
async def mute_del_by_index(session: CommandSession):
    msg = '你要删除一项啊debu'
    global DATA_LIST
    group_list = []
    group_id = session.ctx['group_id']
    DATA_LIST = await get_mute_data()
    for i in range(len(DATA_LIST)):
        item = DATA_LIST[i]
        if group_id == int(item['group_id']):
            group_list.append(i)
            msg = msg + '\n' + str(i+1) + '. ' + 'QQ:' +str(item['user_id']) + ' 群:' + str(item['group_id']) + ' 关键字:' + str(item['key_word']) + ' 时长:' + str([item['mute_time']])
    if len(group_list) == 0:
        await session.finish('这群没有迫害~')
    index = session.get('index', prompt=msg)
    if not (int(index) - 1) in group_list:
        await session.finish('这是隔壁群的，你这是要翻天？')
    result = await del_data_by_index(int(index) - 1)
    if result:
        await session.send('搞定！快夸我！')
    else:
        await session.send('发生错误了baka')


@mute_del_by_index.args_parser
async def mdbi_parser(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg == 'stop':
        session.finish('强制结束手冲')
    if session.current_key == 'index':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not tools.is_int(stripped_arg):
            session.pause('哈？你觉得这个像数字吗？')

@on_command('add_mute', aliases = ('添加迫害', '迫害添加'), permission=perm.GROUP_ADMIN)
async def add_mute(session: CommandSession):
    global DATA_LIST
    ctx = session.ctx.copy()
    if DATA_LIST == None:
        DATA_LIST = await get_mute_data()
    user_id = session.get('user_id', prompt='你要指定迫害哪个QQ的死宅啊？（是直接发送Q号，否则回单字否，否字会写吧）')
    if not 'group_id' in ctx:
        group_id = session.get('group_id', prompt='你丫的要不要指定在哪个QQ群迫害？（是直接发送群号，否则回单字否，否字会写吧）')
    else: 
        group_id = ctx['group_id']
    # if (group_id == None and user_id == None) :
    #     session.finish('QQ号和Q群必须填一个！强制终止手冲')
    key_word = session.get('key_word', prompt='赶紧输入迫害关键字啊debu，用‘|’分隔，如‘死宅|真的|恶心’')
    mute_time = session.get('message', prompt='口多久？（单位秒 60~2591999）')
    new_dict = {
        'user_id' : user_id,
        'group_id' : group_id,
        'key_word' : key_word,
        'mute_time' : mute_time
    }
    result = await add_mute_data(new_dict)
    DATA_LIST = await get_mute_data()
    if result:
        await session.send('诺，搞定了，真麻烦')
    else:
        await session.send('发生错误！')

@add_mute.args_parser
async def am_parser(session: CommandSession):
    global DATA_LIST
    if DATA_LIST == None:
        DATA_LIST = await get_mute_data()
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg == 'stop':
        session.finish('强制结束手冲')


    if session.current_key == 'user_id':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not (tools.is_int(stripped_arg) or stripped_arg == '否'):
            session.pause('哈？你觉得这个像QQ号吗？')
        if stripped_arg == '否':
            session.state['user_id'] = None
        if tools.is_int(stripped_arg):
            session.state['user_id'] = int(stripped_arg)

    if session.current_key == 'group_id':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not (tools.is_int(stripped_arg) or stripped_arg == '否'):
            session.pause('哈？你觉得这个像群号吗？')
        if stripped_arg == '否':
            session.state['group_id'] = None
        if tools.is_int(stripped_arg):
            session.state['group_id'] = int(stripped_arg)



    if session.current_key == 'key_word':
        if not stripped_arg:
            session.pause('你丫的关键字呢')

    if session.current_key == 'mute_time':
        if not tools.is_int(stripped_arg):
            session.pause('哈？你觉得这个像时间吗？')
        else:
            if int(stripped_arg) > 2591999 and int(stripped_arg) < 60:
                session.pause('时间范围都不会看的吗baka！')
            if tools.is_int(stripped_arg):
                session.state['mute_time'] = int(stripped_arg)

            
bot = nonebot.get_bot()
@bot.on_message('group')
async def handle_group_message(ctx: Context_T):
    global bot
    #检测禁言
    if ctx['user_id'] == 1000000:
        raw_message = ctx['raw_message']
        if '禁言' in raw_message:
            banned_id = 0
            if not '(' in raw_message:
                banned_id = int(raw_message[0: raw_message.rfind('被管理员') - 1])
            else:
                banned_id = int(raw_message[raw_message.find('(') + 1: raw_message.rfind(')')])
            if '解除' in raw_message:
                pass
            else:
                susers = global_var.get_super_users()
                if banned_id in susers:
                    msg_ctx = ctx.copy()
                    msg_ctx['message'] = 'bot帕里你怎么又被塞住了，我来帮帮你吧（猛地抽出！）'
                    await bot.send_msg(**msg_ctx)
                    await bot.set_group_ban(group_id=ctx['group_id'], user_id=banned_id, duration=0)
                    msg_ctx['message'] = '好了，料金10000円？'
                    await bot.send_msg(**msg_ctx)
                
    global DATA_LIST
    if DATA_LIST == None:
        DATA_LIST = await get_mute_data()
    found_it = False
    for item in DATA_LIST:
        item_qq = None
        if item['user_id']:
            item_qq = int(item['user_id'])
        item_qun = None
        if item['group_id']:
            item_qun = int(item['group_id'])
        if (ctx['group_id'] == item_qun and ctx['user_id'] == item_qq) or (item_qun == None and ctx['user_id'] == item_qq) or (item_qq == None and ctx['group_id'] == item_qun):
            nickname = ''
            if 'card' in ctx['sender']:
                if ctx['sender']['card'] != '':
                    nickname = ctx['sender']['card']
                else:
                    nickname = ctx['sender']['nickname'] 
            else:
                nickname = ctx['sender']['nickname']
            key_words_str = item['key_word']
            if key_words_str == '*':
                await bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=int(item['mute_time']))
                message = '%s迫害成功'%nickname
                await bot.send_msg(group_id=ctx['group_id'], message=message)
                return
            key_words = key_words_str.split('|')
            for word in key_words:
                if ctx['raw_message'].find(word) >= 0:
                    found_it = True
                    await bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=int(item['mute_time']))
                    
                    message = '%s迫害成功'%nickname
                    await bot.send_msg(group_id=ctx['group_id'], message=message)
            if found_it:
                break
        if found_it:
             break


# @nonebot.scheduler.scheduled_job('cron', minute='*')
async def daily_update(year, month, day, hour, weeknum):
    date_list = [year, month, day, hour, weeknum]
    logger.info('check mute analyze')
    cur_ma_data = await get_mute_analyze_data()
    if not 'update_time' in cur_ma_data:
        cur_ma_data['update_time'] = []
    if date_list == cur_ma_data['update_time']:
        return
    else:
        global bot
        try:
            for key in cur_ma_data:
                if tools.is_int(key):
                    if not 'max_cur_day' in cur_ma_data[key]:
                        continue
                    cur_per = await get_remove_percentage(int(key))
                    day_msg = '本日共发出口球%s，\n本日最佳是%s：%s\n本日最终赦免概率是%s'%(
                        tools.sec_to_str(cur_ma_data[key]['sum_this_day']),
                        '和'.join(cur_ma_data[key]['max_cur_day']['nickname']),
                        tools.sec_to_str(cur_ma_data[key]['max_cur_day']['sec']),
                        str(cur_per / 100000)
                    )
                    await bot.send_group_msg(group_id = int(key), message = day_msg)
                    cur_ma_data[key]['sum_this_day'] = 0
                    cur_ma_data[key]['max_cur_day'] = {}
        except:
            traceback.print_exc()
            logger.error('每日信息发送失败')
        
        if date_list[4] == 1:
            try:
                for key in cur_ma_data:
                    if tools.is_int(key):
                        if not 'max_cur_week' in cur_ma_data[key]:
                            continue
                        week_msg = '本周共发出口球%s，本周最佳是%s：%s'%(
                            tools.sec_to_str(cur_ma_data[key]['sum_this_week']),
                            '和'.join(cur_ma_data[key]['max_cur_week']['nickname']),
                            tools.sec_to_str(cur_ma_data[key]['max_cur_week']['sec'])
                        )
                        await bot.send_group_msg(group_id = int(key), message = week_msg)
                        cur_ma_data[key]['sum_this_week'] = 0
                        cur_ma_data[key]['max_cur_week'] = {}
            except:
                traceback.print_exc()
                logger.error('每周信息发送失败')
        if date_list[2] == 1:
            try:
                for key in cur_ma_data:
                    if tools.is_int(key):
                        if not 'max_cur_month' in cur_ma_data[key]:
                            continue
                        month_msg = '本月共发出口球%s，本月最佳是%s：%s'%(
                            tools.sec_to_str(cur_ma_data[key]['sum_this_month']),
                            '和'.join(cur_ma_data[key]['max_cur_month']['nickname'])
                            ,
                            tools.sec_to_str(cur_ma_data[key]['max_cur_month']['sec'])
                        )
                        await bot.send_group_msg(group_id = int(key), message = month_msg)
                        cur_ma_data[key]['sum_this_month'] = 0
                        cur_ma_data[key]['max_cur_month'] = {}
            except:
                traceback.print_exc()
                logger.error('每月信息发送失败')
        global DEF_REMOVE_MUTE_PERCENTAGE
        if not 'cur_remove_percentage' in cur_ma_data:
            return True
        for key in cur_ma_data['cur_remove_percentage']:
            cur_ma_data['cur_remove_percentage'][key] = DEF_REMOVE_MUTE_PERCENTAGE
        cur_ma_data['update_time'] = date_list
        await write_mute_analyze_data(cur_ma_data)

@on_command('mute_analyze', aliases = ('口球统计', '统计口球'), permission=perm.GROUP_MEMBER)
@check_black_list()
async def mute_analyze(session: CommandSession):
    ctx = session.ctx.copy()
    if not 'group_id' in ctx:
        return
    group_id = ctx['group_id']
    ma_data = await get_mute_analyze_data()
    if not str(group_id) in ma_data:
        await session.send('本群暂时未派发过口球！')
        return
    group_data = ma_data[str(group_id)]
    if group_data:
        cur_day_str = tools.sec_to_str(group_data['sum_this_day'])
        cur_week_str = tools.sec_to_str(group_data['sum_this_week'])
        cur_month_str = tools.sec_to_str(group_data['sum_this_month'])
        msg = '本群口球信息：\n今天派发口球总数为%s\n本周派发口球总数为%s\n本月派发口球总数为%s'%(cur_day_str, cur_week_str, cur_month_str)
        try:
            max_day_data = group_data['max_cur_day']
            max_week_data = group_data['max_cur_week']
            max_month_data = group_data['max_cur_month']
            msg = msg + '\n今日最佳：%s：%s\n本周最佳：%s：%s\n本月最佳：%s：%s'%(
                '和'.join(max_day_data['nickname']),
                tools.sec_to_str(int(max_day_data['sec'])),
                '和'.join(max_week_data['nickname']),
                tools.sec_to_str(int(max_week_data['sec'])),
                '和'.join(max_month_data['nickname']),
                tools.sec_to_str(int(max_month_data['sec'])),
                )
        except:
            pass
        await session.send(msg)

@on_natural_language(keywords={'口球'})
@check_black_list()
async def nl_mute_draw(session: NLPSession):
    # mute_time = random.randint(60, 2591999)
    # mute_time = random.randint(60, 1200)
    mute_time = 0
    ctx = session.ctx.copy()
    raw_msg = ctx['raw_message']
    if '终极' in raw_msg:
        mute_time = random.randint(60, 2591999)
    elif '大' in raw_msg:
        mute_time = random.randint(60, 86400)
    elif '睡眠' in raw_msg:
        mute_time = random.randint(60, 8*60*60)
    else:
        mute_time = random.randint(60, 1800)
    bot = session.bot
    mute_min = math.floor(mute_time / 60)
    mute_time = mute_min * 60
    mute_str = tools.sec_to_str(mute_time)
    await bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=mute_time)
    nickname = ''
    if 'card' in ctx['sender']:
        if ctx['sender']['card'] != '':
            nickname = ctx['sender']['card']
        else:
            nickname = ctx['sender']['nickname'] 
    else:
        nickname = ctx['sender']['nickname']
    await add_mute_analyze_time(mute_time, ctx['group_id'])
    max_result = 0
    if not (ctx['sender']['role'] == 'owner' or ctx['sender']['role'] == 'admin'):
        message = '恭喜%s抽取到%s的口球！'%(nickname, mute_str)
        max_result = await compare_mute_time(sec = mute_time, user_id = ctx['user_id'], group_id = ctx['group_id'], nickname = nickname)
        if max_result == 1:
            message = message + '\n并且刷新今日最佳！'
        elif max_result == 11:
            message = message + '\n并且持平了今日最佳！'
        elif max_result == 2:
            message = message + '\n并且刷新本周最佳！'
        elif max_result == 21:
            message = message + '\n并且持平了本周最佳！'
        elif max_result == 3:
            message = message + '\n并且刷新本月最佳！'
        elif max_result == 31:
            message = message + '\n并且持平了本月最佳！'
        await bot.send_msg(group_id=ctx['group_id'], message=message)
        # rand_num = random.randint(0, 999)
        rand_num = random.randint(0, 9999999)
        cur_per = await get_remove_percentage(ctx['group_id'])
        if rand_num <= cur_per:
            msg = 'mea捏，突然觉得心情好，所以还是给%s你解除了吧（按进去让你吞下）'%nickname
            await bot.send_msg(group_id=ctx['group_id'], message=msg)
            await bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=0)
            msg = '%s你开心吧？记得下次直播的时候打钱哦~~'%nickname
            await bot.send_msg(group_id=ctx['group_id'], message=msg)
            new_value = cur_per - math.floor(mute_time / 60) * 65
            if new_value < 0:
                new_value = 0
            await update_remove_percentage(group_id = ctx['group_id'], new_value = new_value)
        else:
            await update_remove_percentage(group_id = ctx['group_id'], new_value = cur_per + math.floor(mute_time / 60) * 65)
    else:
        await session.send('管理员也来凑热闹？不行哦~')


@on_command('get_remove_mute_percentage', aliases = ('当前豁免几率', '当前赦免概率'), permission=perm.GROUP_MEMBER)
@check_black_list()
async def get_remove_mute_percentage(session: CommandSession):
    ctx = session.ctx.copy()
    cur_per = await get_remove_percentage(group_id = ctx['group_id'])
    await session.send('当前被饶恕的几率是' + str(cur_per/100000) + '%哦')

@on_command('update_remove_percentage_c', aliases = ('更新豁免几率', '更新赦免概率'), permission=perm.SUPERUSER)
@check_black_list()
async def update_remove_percentage_c(session: CommandSession):
    ctx = session.ctx.copy()
    if not 'group_id' in ctx:
        return
    new_value = session.get('new_value', prompt = '新的参数是？')
    result = await update_remove_percentage(group_id = ctx['group_id'], new_value = new_value)
    if result:
        await session.send('成功！')
    else:
        await session.send('发生错误！')

@update_remove_percentage_c.args_parser
async def urpc_parser(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg and tools.is_int(stripped_arg):
            session.state['new_value'] = math.floor(int(stripped_arg) * 100000)
            return
    else:
        if tools.is_int(stripped_arg):
            session.state['new_value'] = math.floor(int(stripped_arg) * 100000)
            return
        session.finish('参数有错！')

@on_natural_language(keywords={'献祭自己', '我来做祭品'})
@check_black_list()
async def sacrifice_mute(session: NLPSession):
    mute_time = 3600
    # mute_time = random.randint(60, 1200)
    ctx = session.ctx.copy()
    bot = session.bot
    mute_min = math.floor(mute_time / 60)
    mute_time = mute_min * 60
    mute_hour = math.floor(mute_min / 60)
    mute_day = math.floor(mute_hour / 24)
    mute_hour = mute_hour - mute_day * 24
    mute_min = mute_min - mute_hour * 60 - mute_day * 24 * 60
    mute_str = ''
    if mute_day > 0:
        mute_str = mute_str + '%d天'%mute_day
    if mute_hour > 0:
        mute_str = mute_str + '%d小时'%mute_hour
    if mute_min > 0:
        mute_str = mute_str + '%d分钟'%mute_min
    await bot.set_group_ban(group_id=ctx['group_id'], user_id=ctx['user_id'], duration=mute_time)
    nickname = ''
    if 'card' in ctx['sender']:
        if ctx['sender']['card'] != '':
            nickname = ctx['sender']['card']
        else:
            nickname = ctx['sender']['nickname'] 
    else:
        nickname = ctx['sender']['nickname']
    message = '你上祭坛了，我不一定播，以上！'
    await bot.send_msg(group_id=ctx['group_id'], message=message)

@on_command('remove_all_mute', aliases = ('大赦天下', '全部解除口球'), permission=perm.GROUP_ADMIN)
async def remove_all_mute(session: CommandSession):
    bot = session.bot
    ctx = session.ctx.copy()
    await remove_all_mute_public(ctx['group_id'])


async def remove_all_mute_public(group_id: int):
    group_list = await bot.get_group_member_list(group_id=group_id)
    for item in group_list:
        is_ignore = False
        if 'card' in item:
            card = item['card']
            global REMOVE_IGNORE_LIST
            for i_item in REMOVE_IGNORE_LIST:
                if i_item in card:
                    is_ignore = True
        if not is_ignore:
            await bot.set_group_ban(group_id=group_id, user_id=item['user_id'], duration=0)

@on_command('admin_draw', aliases = ('代抽口球', '口球代抽'), permission=perm.GROUP_ADMIN)
async def admin_draw(session: CommandSession):
    # mute_time = random.randint(60, 2591999)
    mute_time = random.randint(60, 1200)
    ctx = session.ctx.copy()
    bot = session.bot
    mute_min = math.floor(mute_time / 60)
    mute_time = mute_min * 60
    mute_str = tools.sec_to_str(mute_time)
    
    user_id = session.get('user_id', prompt='让哪个debu抽奖？（Q号或者昵称搜索）')
    if user_id:
        if type(user_id) == int:
            await bot.set_group_ban(group_id=ctx['group_id'], user_id=user_id, duration=mute_time)
            cur_info = await bot.get_group_member_info(group_id=ctx['group_id'], user_id =user_id)
            nickname = ''
            if 'card' in cur_info:
                if cur_info['card'] != '':
                    nickname = cur_info['card']
                else:
                    nickname = cur_info['nickname'] 
            else:
                nickname = cur_info['nickname']
            await add_mute_analyze_time(mute_time, ctx['group_id'])
            message = '恭喜%s抽取到%s的口球！'%(nickname, mute_str)
            # max_result = await compare_mute_time(sec = mute_time, user_id = ctx['user_id'], group_id = ctx['group_id'], nickname = nickname)
            message = '恭喜%s抽取到%s的口球！'%(nickname, mute_str)
            # if max_result == 1:
            #     message = message + '\n并且刷新今日最佳！'
            # elif max_result == 11:
            #     message = message + '\n并且持平了今日最佳！'
            # elif max_result == 2:
            #     message = message + '\n并且刷新本周最佳！'
            # elif max_result == 21:
            #     message = message + '\n并且持平了本周最佳！'
            # elif max_result == 3:
            #     message = message + '\n并且刷新本月最佳！'
            # elif max_result == 31:
            #     message = message + '\n并且持平了本月最佳！'
            await bot.send_msg(group_id=ctx['group_id'], message=message)
        elif type(user_id) == list:
            for item in user_id:
                await bot.set_group_ban(group_id=ctx['group_id'], user_id=item, duration=mute_time)
                cur_info = await bot.get_group_member_info(group_id=ctx['group_id'], user_id=item)
                nickname = ''
                if 'card' in cur_info:
                    if cur_info['card'] != '':
                        nickname = cur_info['card']
                    else:
                        nickname = cur_info['nickname'] 
                else:
                    nickname = cur_info['nickname']
                message = '恭喜%s抽取到%s的口球！'%(nickname, mute_str)
                await add_mute_analyze_time(mute_time, ctx['group_id'])
                # max_result = await compare_mute_time(sec = mute_time, user_id = ctx['user_id'], group_id = ctx['group_id'], nickname = nickname)
                message = '恭喜%s抽取到%s的口球！'%(nickname, mute_str)
                # if max_result == 1:
                #     message = message + '\n并且刷新今日最佳！'
                # elif max_result == 11:
                #     message = message + '\n并且持平了今日最佳！'
                # elif max_result == 2:
                #     message = message + '\n并且刷新本周最佳！'
                # elif max_result == 21:
                #     message = message + '\n并且持平了本周最佳！'
                # elif max_result == 3:
                #     message = message + '\n并且刷新本月最佳！'
                # elif max_result == 31:
                #     message = message + '\n并且持平了本月最佳！'
                await bot.send_msg(group_id=ctx['group_id'], message=message)
    else:
        await bot.send_msg(group_id=ctx['group_id'], message='查无此人！！baka')


@admin_draw.args_parser
async def ad_parser(session: CommandSession):
    ctx = session.ctx.copy()
    group_id = ctx['group_id']
    bot = session.bot
    qun_info = await bot.get_group_member_list(group_id=group_id)
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg:
        if session.is_first_run or session.current_key == 'user_id':
            if tools.is_int(stripped_arg):
                user_id = int(stripped_arg)
                is_in_group = False
                for item in qun_info:
                    if user_id == item['user_id']:
                        is_in_group = True
                if not is_in_group:
                    user_id = False
                session.state['user_id'] = user_id
            else:
                user_id = []
                for item in qun_info:
                    nickname = ''
                    if 'card' in item:
                        if item['card'] != '':
                            nickname = item['card']
                        else:
                            nickname = item['nickname'] 
                    else:
                        nickname = item['nickname']
                    if not nickname.find(stripped_arg) == -1:
                        user_id.append(item['user_id'])
                session.state['user_id'] = user_id


check_file()

example =[
    {
        'user_id' : 111111111,
        'group_id' : 222222222,
        'key_word' : '233',
        'mute_time' : 222
    },
    {
        'user_id' : 111111111,
        'group_id' : 222222222,
        'key_word' : '233',
        'mute_time' : 222
    },
]
