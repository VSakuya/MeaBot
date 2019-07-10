
from nonebot import on_command, CommandSession, permission as perm
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import Message, MessageSegment
from nonebot.typing import Context_T
import nonebot

from .data_source import *
from functions import special_user
from functions import tools


__plugin_name__ = '高级用户'
__plugin_usage__ = r"""高级用户的管理
指令：
添加内测用户/内测用户添加 （bot管理员）
添加直播通知用户/直播通知用户添加 （bot管理员）
添加赞助用户/赞助用户添加 （bot管理员）
添加自回审核用户/自回审核用户添加 （bot管理员）"""

@on_command('add_alpha_test_user', aliases = ('添加内测用户', '内测用户添加'), permission=perm.SUPERUSER)
async def add_alpha_test_user(session: CommandSession):
    member_list = await special_user.get_alpha_test_list()
    new_member = session.get('new_member', prompt='内测新成员的Q号？')
    if new_member in member_list:
        session.finish('Ta已经在名单里了！')
    else:
        result = await special_user.add_alpha_test_user(int(new_member))
        if result:
            session.finish('搞定，快夸我！')
        else:
            session.finish('发生错误啦！')

@add_alpha_test_user.args_parser
async def aatu_parser(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg == 'stop':
        session.finish('强制结束手冲')
    if session.current_key == 'new_member':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not tools.is_int(stripped_arg):
            session.pause('哈？你觉得这个像Q号吗？')
        session.state['new_member'] = int(stripped_arg)

@on_command('add_live_alert_user', aliases = ('添加直播通知用户', '直播通知用户添加'), permission=perm.SUPERUSER)
async def add_live_alert_user(session: CommandSession):
    member_list = await special_user.get_live_alert_list()
    new_member = session.get('new_member', prompt='要被大吵大闹的新成员Q号是？')
    if new_member in member_list:
        session.finish('Ta已经在名单里了！')
    else:
        result = await special_user.add_live_alert_user(int(new_member))
        if result:
            session.finish('搞定，快夸我！')
        else:
            session.finish('发生错误啦！')

@add_live_alert_user.args_parser
async def alau_parser(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg == 'stop':
        session.finish('强制结束手冲')
    if session.current_key == 'new_member':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not tools.is_int(stripped_arg):
            session.pause('哈？你觉得这个像Q号吗？')
        session.state['new_member'] = int(stripped_arg)

@on_command('add_sponsor_user', aliases = ('添加赞助用户', '赞助用户添加'), permission=perm.SUPERUSER)
async def add_sponsor_user(session: CommandSession):
    member_list = await special_user.get_sponsor_list()
    new_member = session.get('new_member', prompt='帮助我们的好哥哥的Q号是？')
    if new_member in member_list:
        session.finish('Ta已经在名单里了！')
    else:
        result = await special_user.add_sponsor_user(int(new_member))
        if result:
            session.finish('搞定，快夸我！')
        else:
            session.finish('发生错误啦！')

@add_sponsor_user.args_parser
async def asu_parser(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg == 'stop':
        session.finish('强制结束手冲')
    if session.current_key == 'new_member':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not tools.is_int(stripped_arg):
            session.pause('哈？你觉得这个像Q号吗？')
        session.state['new_member'] = int(stripped_arg)

@on_command('add_auto_reply_checker_user', aliases = ('添加自回审核用户', '自回审核用户添加'), permission=perm.SUPERUSER)
async def add_auto_reply_checker_user(session: CommandSession):
    bot = session.bot
    add_group = session.get('add_group', prompt='需要指定qq群吗？（是直接发送群号，否则回单字否，否字会写吧，或者回本群）')
    rc_data = await special_user.get_auto_reply_checker_data()
    new_member = session.get('new_member', prompt='新进的审核员的Q号是？')
    if not add_group:
        group_list = await bot.get_group_list()
        result = True
        for item in group_list:
            result = await special_user.add_auto_reply_checker_user(new_id = int(new_member), group_id = int(item['group_id']))
        if result:
            session.finish('搞定，快夸我！')
        else:
            session.finish('发生错误啦！')
    else:
        if rc_data and int(new_member) in rc_data[str(add_group)]:
            session.finish('Ta已经在名单里了！')
        else:
            result = await special_user.add_auto_reply_checker_user(new_id=int(new_member), group_id = int(add_group))
            if result:
                session.finish('搞定，快夸我！')
            else:
                session.finish('发生错误啦！')    


@add_auto_reply_checker_user.args_parser
async def aarcu_parser(session: CommandSession):
    bot = session.bot
    ctx = session.ctx.copy()
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg == 'stop':
        session.finish('强制结束手冲')

    if session.current_key == 'add_group':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not (tools.is_int(stripped_arg) or stripped_arg == '否' or stripped_arg == '本群'):
            session.pause('哈？你觉得这个像群号吗？')
        else:
            if stripped_arg == '否':
                session.state['add_group'] = 0
            elif stripped_arg == '本群':
                session.state['add_group'] = ctx['group_id']
            else:
                group_list = await bot.get_group_list()
                is_in_group = False
                for item in group_list:
                    if int(item['group_id']) == int(stripped_arg):
                        is_in_group = True
                if not is_in_group:
                    session.pause('我没有加入这个群！！')
                session.state['add_group'] = int(stripped_arg)

    if session.current_key == 'new_member':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not tools.is_int(stripped_arg):
            session.pause('哈？你觉得这个像Q号吗？')
        session.state['new_member'] = int(stripped_arg)

bot = nonebot.get_bot()
@bot.on_request('friend')
async def handle_friend_message(ctx: Context_T):
    print(ctx)
    allow_friend_list = await special_user.get_allowed_friend_list()
    if ctx['user_id'] in allow_friend_list:
            await bot.set_friend_add_request(flag=ctx['flag'], approve=True)


check_file()

    