import nonebot
from nonebot import on_command, CommandSession, permission as perm
from nonebot import Message, MessageSegment
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import urllib.request
import urllib.parse
from config import global_var
from aiocqhttp import exceptions
from functions import *

@on_command('test', aliases=['测试', 'test'], permission=perm.SUPERUSER)
async def _(session: CommandSession):
    bot = session.bot
    ctx = session.ctx.copy()
    # print(global_var.get_super_users())
    # urllib.request.urlretrieve('https://c2cpicdw.qpic.cn/offpic_new/904853953//8a156d0f-5f4c-4406-8f79-f5ea543a5767/0?vuin=2482883152&amp;term=2', 'F:\QQBot\CQP-xiaoi\酷Q Pro\data\image\\reply\\' + '%d.jpg' % round(int(time.time() * 1000)))
    # ctx['message'] = MessageSegment.image('/reply/1562313712004.gif')
    # await bot.send_msg(**ctx)
    # await black_list.add_black_list_data(233333)
    # a = await black_list.get_black_list_data()
    # print(a)
    # print(await black_list.is_black_list(233))
    # g_list = []
    # try:
    #     g_list = await bot.get_group_list()
    # except exceptions.ActionFailed as e:
    #     print(e)
    
    # print(g_list)
    # af_list = await special_user.get_allowed_friend_list()
    # print(af_list)
    # a = [1,2,3]
    # b = [2,3,4] 
    # print(a + b)#[1, 2, 3, 2, 3, 4]
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    print(now.day)
    print(now.month)
    print(datetime.isoweekday(now))
    pass