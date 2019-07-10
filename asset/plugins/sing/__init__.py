import asyncio
import random
from nonebot import on_command, CommandSession, permission as perm
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import Message, MessageSegment

from .data_source import *
from functions import tools

__plugin_name__ = '唱歌'
__plugin_usage__ = r"""根据网易云音乐黒羽翼堕天的电台《神楽mea的清楚time》选取歌曲播放
指令：
唱 （任何人，带搜索功能，可输入歌名单字，也可输入“mea唱随机”来随机播放

！更新曲库/曲库更新 (bot管理员)"""

DATA_LIST = None

@on_command('song_update', aliases = ('更新曲库', '曲库更新'), permission=perm.SUPERUSER)
async def song_update(session: CommandSession):
    await update_songs()
    DATA_LIST = await get_sing_data()
    await session.send('更新完毕，现在mea一共会唱%s首歌！'%len(DATA_LIST))

@on_command('sing', permission=perm.GROUP_MEMBER)
async def sing(session: CommandSession):
    song_name = session.get('song_name', prompt='你要我唱啥？')
    ctx = session.ctx.copy()
    bot = session.bot
    if song_name == '随机':
        all_song_list = await get_sing_data()
        max_count = len(all_song_list)
        index = random.randint(0, int(max_count - 1))
        song_name = all_song_list[index]
        song_dir = get_file_CQ_dir(song_name)
        del ctx['message']
        print(song_dir)
        await bot.send_msg(**ctx, message = song_name[0: song_name.rfind('.')])
        await bot.send_msg(**ctx, message = [{'type': 'record', 'data': {'file': song_dir}}])
    else:
        song_list = await search_songs(song_name)
        if len(song_list) > 1:
            song_str = '你要听哪首啊（嫌弃） \n'
            for i in range(len(song_list)):
                song_name = song_list[i]
                # song_name = song_name.replace('.mp3', '')
                dot_index = song_name.rfind('.')
                song_name = song_name[0: dot_index]
                song_name = song_name.strip()
                song_str = song_str + str(i+1) + '. ' + song_name + '\n'
            song_index = session.get('song_index', prompt=song_str)
            song_dir = get_file_CQ_dir(song_list[int(song_index) - 1])
            del ctx['message']
            song_name = song_list[int(song_index) - 1]
            await bot.send_msg(**ctx, message = song_name[0: song_name.rfind('.')])
            await bot.send_msg(**ctx, message = [{'type': 'record', 'data': {'file': song_dir}}])
        elif len(song_list) == 1:
            song_name = song_list[0]
            song_dir = get_file_CQ_dir(song_name)
            del ctx['message']
            print(song_dir)
            await bot.send_msg(**ctx, message = song_name[0: song_name.rfind('.')])
            await bot.send_msg(**ctx, message = [{'type': 'record', 'data': {'file': song_dir}}])
        else:
            await session.send('不会唱这个！')
            pass

@sing.args_parser
async def s_parser(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['song_name'] = stripped_arg
        return
    if session.current_key == 'song_index':
        if not stripped_arg:
            session.pause('你哑巴了嘛')
        if not tools.is_int(stripped_arg):
            session.pause('哈？数字！数字懂吗？3x7=27')

@on_natural_language(keywords={'唱'})
async def sing_nl(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    name = stripped_msg.replace('唱', '')

    return IntentCommand(90.0, 'sing', current_arg=name or '')


check_file()