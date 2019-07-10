import nonebot
from nonebot import on_command, CommandSession, permission as perm

HELP_TEXT = """Mea bot by VSakuya
在群内对Mea bot输入指令可以直接艾特或者需要呼叫名，如“mea唱烟草”，“mea！帮助”，私聊则不用带呼号
现在支持呼叫名“mea”, “Mea”，“神楽めあ”，“めあちゃん”，“咩”
现在拥有功能（使用“！帮助 功能名”如“！帮助 唱歌”查看详情）：
连续对话型指令输入“stop”可以终止"""

@on_command('usage', aliases=['使用帮助', '帮助', '使用方法'], permission=perm.EVERYBODY)
async def _(session: CommandSession):
    # 获取设置了名称的插件列表
    plugins = list(filter(lambda p: p.name, nonebot.get_loaded_plugins()))
    global HELP_TEXT
    arg = session.current_arg_text.strip().lower()
    if not arg:
        # 如果用户没有发送参数，则发送功能列表
        await session.send(
            HELP_TEXT + '\n' + '\n'.join(p.name for p in plugins))
        return

    # 如果发了参数则发送相应命令的使用帮助
    for p in plugins:
        if p.name.lower() == arg:
            await session.send(p.usage)
