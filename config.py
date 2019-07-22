import os
from nonebot.default_config import *

SUPERUSERS = {904853953}
COMMAND_START = {'/', '!', '／', '！'}
NICKNAME = {'mea', 'Mea', '神楽めあ', 'めあちゃん', '咩'}
# HOST = '127.0.0.1'
# PORT = 8080
HOST = '172.17.0.1'
PORT = 2333

class global_var:
    # COOLQ_DIR = 'F:\QQBot\CQP-xiaoi\酷Q Pro'
    COOLQ_DIR = '/root/coolq'
    NECESSARY_DIR_LIST = [
        os.path.join(COOLQ_DIR, 'data', 'record', 'music'),
        os.path.join(COOLQ_DIR, 'data', 'record', 'sound'),
        os.path.join(COOLQ_DIR, 'data', 'image', 'reply')
    ]
    
    @staticmethod
    def get_coolq_dir() -> str: 
        return global_var.COOLQ_DIR

    @staticmethod
    def get_necessary_dir() -> list: 
        return global_var.NECESSARY_DIR_LIST

    @staticmethod
    def get_super_users() -> set:
        global SUPERUSERS
        return SUPERUSERS