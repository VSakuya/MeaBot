import asyncio
import time

from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand, permission as perm
from nonebot import Message, MessageSegment

from .data_source import *
from config import global_var
from functions import black_list
from functions import tools
from functions import special_user
__plugin_name__ = '自动回复'
__plugin_usage__ = r"""任何人都能轻松提交的自动回复
提交音频请将音频（mp3即可）以及关键字发送给VSakuya
任何提交违规内容的人将会被bot永久拉黑！
命令：
！添加自动回复/自动回复添加 （群成员 该功能仅支持图文）
！自动回复列表/列表自动回复 （群成员）
！审核自回/审核自动回复 （bot管理员）
！同意自回/同意自动回复 （bot管理员 指令[空格]+申请ID）
！更新回复音效/更新回音 （bot管理员）"""

IS_CHECKING = False
CURRENT_CHECKING_USER = 0



@on_command('add_autoreply', aliases = ('添加自动回复', '自动回复添加'), permission=perm.GROUP_MEMBER)
async def add_autoreply(session: CommandSession):
    ctx = session.ctx.copy()
    bot = session.bot
    user_id = ctx['user_id']
    if await black_list.is_black_list(user_id):
        ctx_t = ctx
        ctx_t['message'] = '你已被拉黑'
        await bot.send_msg(**ctx_t)
        return
    
    #获取昵称
    nickname = ''
    if 'group_id' in ctx:
        cur_info = await bot.get_group_member_info(group_id=ctx['group_id'], user_id=ctx['user_id'])
        if 'card' in cur_info:
            if cur_info['card'] != '':
                nickname = cur_info['card']
            else:
                nickname = cur_info['nickname'] 
        else:
            nickname = cur_info['nickname']
    else:
        cur_info = await bot.get_stranger_info(user_id = ctx['user_id'])
        nickname = cur_info['nickname']

    key_word = session.get('key_word', prompt='赶紧输入关键字啊，' + nickname + '你这个debu，用‘|’分隔，如‘死宅|真的|恶心’')

    group_id = 0
    if 'group_id' in ctx:
        group_id = ctx['group_id']
    else:
        group_id = session.get('group_id', prompt= nickname + '你丫的要不要指定QQ群（是直接发送群号，否则回单字否，否字会写吧）')
    message = session.get('message', prompt='自动回复内容是啥啊'+ nickname +'（仅支持文字与图片组合）：')

    result = await add_reply_t_data(key = key_word ,group_id = group_id, message= message, submit_user_id = ctx['user_id'])
    if result:
        await session.send('诺，搞定了，真麻烦\n' + nickname + '你的申请已经提交上去啦\n' + '申请id是：' + str(result) + '\n' + '请等待bot管理员那懒狗审核')
        temp_list = await get_key_t_list()
        count = len(temp_list)
        if not group_id:
            super_user = global_var.get_super_users()
            for user in super_user:
                await bot.send_private_msg(user_id = user, message = Message(str(ctx['user_id']) + '提交了针对群：' + str(group_id) + '的自动回复关键字“' + key_word + '”的自动回复申请，当前还有' + str(count) + '个申请尚未处理！'))
        else:
            check_users = await special_user.get_auto_reply_checker_data_by_group_id(int(group_id))
            for user in check_users:
                await bot.send_private_msg(user_id = user, message = Message(str(ctx['user_id']) + '提交了针对群：' + str(group_id) + '的自动回复关键字“' + key_word + '”的自动回复申请，当前还有' + str(count) + '个申请尚未处理！'))
    else:
        await session.send('发生错误！')

@add_autoreply.args_parser
async def aa_parser(session: CommandSession):
    key_list = await get_key_list()
    key_t_list = await get_key_t_list()
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['key_word'] = stripped_arg
        return
    if stripped_arg == 'stop':
        session.finish('强制结束手冲')

    if session.current_key == 'key_word':
        if not stripped_arg:
            session.pause('你丫的关键字呢')
        has_same_set = False
        same_key_set = None
        
        in_keys = stripped_arg.split('|')
        for own_key_list in key_list:
            own_keys = own_key_list.split('|')
            for own_key in own_keys:
                for in_key in in_keys:
                    if own_key == in_key:
                        has_same_set = True
                        same_key_set = own_key
                        break
                if has_same_set:
                    break
            if has_same_set:
                break

        if has_same_set:  
            session.pause('‘%s’这个关键字早就有设置啦你这个屑，重写' % same_key_set)

        has_same_temp = False
        same_key_temp = None
        
        in_keys = stripped_arg.split('|')
        for own_key_list in key_t_list:
            own_keys = own_key_list.split('|')
            for own_key in own_keys:
                for in_key in in_keys:
                    if own_key == in_key:
                        has_same_temp = True
                        same_key_temp = own_key
                        break
                if has_same_temp:
                    break
            if has_same_temp:
                break

        if has_same_temp:  
            session.pause('‘%s’这个关键字已经在申请啦，重写' % same_key_temp)

    if session.current_key == 'group_id':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not (tools.is_int(stripped_arg) or stripped_arg == '否'):
            session.pause('哈？你觉得这个像群号吗？')
        if tools.is_int(stripped_arg):
            session.state['group_id'] = int(stripped_arg)
        if stripped_arg == '否':
            session.state['group_id'] = 0

    if session.current_key == 'message':
        print(session.ctx['message'])
        new_msg = await meassage_convert(session.ctx['message'], session.ctx['raw_message'])
        if not new_msg:
            session.finish('发生未知错误！！结束当前进程！')
        session.state['message'] = new_msg

@on_command('list_ar', aliases = ('自动回复列表', '列表自动回复'), permission=perm.GROUP_MEMBER)
async def list_ar(session: CommandSession):
    key_list = await get_key_list()
    sound_list = await get_sound_data()
    data_str = '目前图文自动回复有：\n'
    for i in range(len(key_list)):
        item = key_list[i]
        data_str = data_str + item + '/'
    data_str = data_str + '\n\n目前语音自动回复有：\n'
    for item in sound_list:
        sound_name = item[0: item.find('.')]
        if '_' in sound_name:
            sounds = sound_name.split('_')
            for item_sound in sounds:
                data_str = data_str + item_sound + '/'
        else:
            data_str = data_str + sound_name + '/'
    await session.send(data_str)

# status:
# 0: 否
# 1: 是
# 2: 拉黑
@on_command('start_check', aliases = ('审核自回', '审核自动回复'), permission=perm.EVERYBODY)
async def start_check(session: CommandSession):
    ctx = session.ctx.copy()
    if 'group_id' in ctx:
        return
    
    global IS_CHECKING
    global CURRENT_CHECKING_USER
    if session.is_first_run:
        if IS_CHECKING:
            msg = '当前用户%d正在审核！请稍后再试！'%CURRENT_CHECKING_USER
            session.finish(msg)
            return

    user_id = ctx['user_id']
    super_users = global_var.get_super_users()
    checkers = await special_user.get_auto_reply_checker_data_by_group_id()
    if not (user_id in super_users or user_id in checkers):
        return
    bot = session.bot
    dict_data = {}
    if user_id in super_users:
        dict_data = await get_reply_t_data()
    else:
        group_list = await special_user.get_auto_reply_checker_group_by_user_id(user_id)
        for group in group_list:
            temp_data = await get_reply_t_data(group_id=int(group))
            for key in temp_data:
                dict_data[key] = temp_data[key]
    if len(dict_data) <= 1:
        ctx_t = ctx
        ctx_t['message'] = '暂时没有需要审核的呢'
        await bot.send_msg(**ctx_t)
        return

    IS_CHECKING = True
    CURRENT_CHECKING_USER = user_id

    for key in dict_data:
        if not key == 'max_id':
            status = None
            item_data = dict_data[key]
            key_word = item_data['key']
            message = item_data['message']
            group_id = item_data['group_id']
            submit_user_id = item_data['submit_user_id']

            if not session.current_key or session.current_key == 'status' + str(int(key) - 1):
                key_str = '用户：' + str(submit_user_id) + '申请群：' + str(group_id) + '的自动回复，关键字：“' + key_word + '”，回复：'
                await bot.send_private_msg(user_id = ctx['user_id'], message = key_str)
                ctx['message'] = message
                is_success = True
                try:
                    await bot.send_msg(**ctx)
                except:
                    is_success = False
                    ctx['message'] = '内容有错误！！！'
                    await bot.send_msg(**ctx)
                if not is_success:
                    await del_reply_t_data(key)
                    continue
            status = session.get('status' + str(key), prompt='是否同意？（是/否/拉黑）')
            if status == 0:
                reason = session.get('reason' + str(key), prompt='为啥啊？给点理由呗')
                session.current_key = None
                result = await del_reply_t_data(key)
                if result:
                    await bot.send_private_msg(user_id = user_id, message = '已成功拒绝')
                    if group_id:
                        await bot.send_group_msg(group_id = group_id, message = MessageSegment.at(user_id = submit_user_id) + Message('你的自动回复申请id：' + str(key) + '，关键字：“' + key_word + '”被拒绝了呢\n理由是：' + reason))
                    else:
                        await bot.send_private_msg(user_id = submit_user_id, message = Message('你的自动回复申请id：' + str(key) + '，关键字：“' + key_word + '”被拒绝了呢\n理由是：' + reason))
                else:
                    await bot.send_private_msg(user_id = user_id, message = '发生错误！')
            elif status == 1:
                session.current_key = None
                del_result = await del_reply_t_data(key)
                result = await add_reply_data(group_id = group_id, key = key_word, message = message, submit_user_id = submit_user_id, checked_user_id = user_id)
                if result and del_result:
                    await bot.send_private_msg(user_id = user_id, message = '已成功同意')

                    if group_id:
                        await bot.send_group_msg(group_id = group_id, message = MessageSegment.at(user_id = submit_user_id) + Message('你的自动回复申请id：' + str(key) + '，关键字：“' + key_word + '”被同意了呢'))
                    else:
                        await bot.send_private_msg(user_id = submit_user_id, message = Message('你的自动回复申请id：' + str(key) + '，关键字：“' + key_word + '”被同意了呢'))
                else:
                    await bot.send_private_msg(user_id = user_id, message = '发生错误！')
            elif status == 2:
                reason = session.get('reason', prompt='为啥啊？给点理由呗')
                session.current_key = None
                bl_result= await black_list.add_black_list_data(submit_user_id)
                result = await del_reply_t_data(key)
                if result and bl_result:
                    await bot.send_private_msg(user_id = user_id, message = '已成功添加黑名单！并且因为违规被永久添加黑名单！！！')
                    
                    if group_id:
                        await bot.send_group_msg(group_id = group_id, message = MessageSegment.at(user_id = submit_user_id) + Message('你的自动回复申请id：' + str(key) + '，关键字：“' + key_word + '”被拒绝了呢！并且因为违规被永久添加黑名单！！！\n理由是：' + reason))
                    else:
                        await bot.send_private_msg(user_id = submit_user_id, message = Message('你的自动回复申请id：' + str(key) + '，关键字：“' + key_word + '”被拒绝了呢！并且因为违规被永久添加黑名单！！！\n理由是：' + reason))
                else:
                    await bot.send_private_msg(user_id = user_id, message = '发生错误！')
    IS_CHECKING = False

@start_check.args_parser
async def sc_parser(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    global IS_CHECKING
    if stripped_arg == 'stop':
        IS_CHECKING = False
        session.finish('强制结束手冲')
    if str(session.current_key).find('status') > -1:
        if not (stripped_arg == '是' or stripped_arg == '否' or stripped_arg == '拉黑'):
            session.pause('在？你在说啥？')
        else:
            if stripped_arg == '否':
                session.state[str(session.current_key)] = 0
            if stripped_arg == '是':
                session.state[str(session.current_key)] = 1
            if stripped_arg == '拉黑':
                session.state[str(session.current_key)] = 2

@on_command('accept_by_id', aliases = ('同意自回', '同意自动回复'), permission=perm.EVERYBODY)
async def accept_by_id(session: CommandSession):
    ctx = session.ctx.copy()
    bot = session.bot
    user_id = ctx['user_id']
    super_users = global_var.get_super_users()
    checkers = await special_user.get_auto_reply_checker_data_by_group_id()
    if not (user_id in super_users or user_id in checkers):
        return
    form_id = session.get('form_id', prompt='要处理的申请ID的是？')
    dict_data = {}
    if user_id in super_users:
        dict_data = await get_reply_t_data()
    else:
        group_list = await special_user.get_auto_reply_checker_group_by_user_id(user_id)
        for group in group_list:
            temp_data = await get_reply_t_data(group_id=int(group))
            for key in temp_data:
                dict_data[key] = temp_data[key]
    if not str(form_id) in dict_data:
        session.finish('此申请ID不存在！！')
    else:
        del_result = await del_reply_t_data(form_id)
        t_data = dict_data[str(form_id)]
        key_word = t_data['key']
        message = t_data['message']
        group_id = t_data['group_id']
        submit_user_id = t_data['submit_user_id']
        result = await add_reply_data(group_id = group_id, key = key_word, message = message, submit_user_id = submit_user_id, checked_user_id = user_id)
        if result and del_result:
            await session.send('已成功同意')

            if group_id:
                await bot.send_group_msg(group_id = group_id, message = MessageSegment.at(user_id = submit_user_id) + Message('你的自动回复申请id：' + str(form_id) + '，关键字：“' + key_word + '”被同意了呢'))
            else:
                await bot.send_private_msg(user_id = submit_user_id, message = Message('你的自动回复申请id：' + str(form_id) + '，关键字：“' + key_word + '”被同意了呢'))
        else:
            await bot.send_private_msg(user_id = user_id, message = '发生错误！')

@accept_by_id.args_parser
async def abi_parser(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if tools.is_int(stripped_arg):
            session.state['form_id'] = int(stripped_arg)
    if session.current_key == 'form_id':
        if tools.is_int(stripped_arg):
            session.state['form_id'] = int(stripped_arg)
        else:
            session.pause('哈？这个看着像ID吗？')

@on_command('update_sound', aliases = ('更新回复音效', '更新回音'), permission=perm.SUPERUSER)
async def update_sound(session: CommandSession):
    result = await update_sounds()
    ctx = session.ctx.copy()
    bot = session.bot
    if result:
        sound_list = await get_sound_data()
        count = len(sound_list)
        ctx['message'] = '更新成功！现在有%s个自动回复音频'%count
        await bot.send_msg(**ctx)
    else:
        ctx['message'] = '发生错误！'
        await bot.send_msg(**ctx)
        

@on_natural_language()
async def reply_to_nl(session: NLPSession):
    bot = session.bot
    ctx = session.ctx.copy()
    in_str = session.msg_text.strip()
    data_dict = await get_reply_data()
    sound_list = await get_sound_data()
    group_id = None
    if 'group_id' in ctx:
        group_id = ctx['group_id']   
    
    found_it = False
    is_sound = False
    match_key = {}
    if group_id:
        if str(group_id) in data_dict:
            for key in data_dict[str(group_id)]:
                keys = key.split('|')
                for single_key in keys:
                    if in_str.find(single_key) >= 0:
                        found_it = True
                        match_key[single_key] = {'source' : group_id, 'key': key}

    if 'all' in data_dict:
        for key in data_dict['all']:
            keys = key.split('|')
            for single_key in keys:
                if in_str.find(single_key) >= 0:
                    found_it = True
                    match_key[single_key] = {'source' : 'all', 'key': key}
    
    if sound_list:
        for key in sound_list:
            key_pure = key[0: key.find('.')]
            keys = key_pure.split('_')
            for single_key in keys:
                if in_str.find(single_key) >= 0:
                    found_it = True
                    is_sound = True
                    match_key[single_key] = key
    
    if found_it:
        if is_sound:
            sound_name = ''
            temp_key = ''
            i = 0
            for key in match_key:
                if i == 0:
                    temp_key = key
                    sound_name = match_key[key]
                else:
                    if len(key) > len(temp_key):
                        temp_key = key
                        sound_name = match_key[key]
                i += 1
    
            if 'source' in match_key[temp_key]:
                source = str(match_key[str(temp_key)]['source'])
                final_key = str(match_key[str(temp_key)]['key'])
                send_msg = data_dict[source][final_key]['message']
                ctx['message'] = send_msg
                await bot.send_msg(**ctx)
                return

            if group_id:
                await bot.send_group_msg(group_id = group_id, message=MessageSegment.record(os.sep + 'sound' + os.sep + sound_name))
            else:
                await bot.send_private_msg(user_id = ctx['user_id'], message=MessageSegment.record(os.sep + 'sound' + os.sep + sound_name))
        else:
            final_key = ''
            temp_key = ''
            i = 0
            for key in match_key:
                if i == 0:
                    temp_key = key
                    final_key = match_key[key]['key']
                else:
                    if len(key) > len(temp_key):
                        temp_key = key
                        final_key = match_key[key]['key']
                i += 1
            source = str(match_key[str(temp_key)]['source'])
            send_msg = data_dict[source][final_key]['message']
            ctx['message'] = send_msg
            await bot.send_msg(**ctx)
            return
            


check_file()


example ={
    'group_id_1':{
        '你好|早上好|中午好':{
            'group_id': 1111111111,
            'message': {},
            'sumbit_user_id' : 22222222,
            'checked_user_id' : 33333333
        }
    },
    'group_id_2':{
        '222':{}
    },
    'all':{
        '2323':{}
    }
    }
