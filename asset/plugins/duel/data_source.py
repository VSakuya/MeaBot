import json
import os
import re
import platform
from config import global_var

from nonebot import logger

def check_file():
    duel_dir = os.path.join(os.curdir, 'asset', 'data', 'duel.json')
    if not os.path.exists(duel_dir):
        empty_dict = {}
        with open(duel_dir , 'w', encoding='utf-8') as data_json:
            json.dump(empty_dict, data_json, ensure_ascii = False)
            
    logger.info('duel file checked')

async def get_duel_data() -> dict:
    duel_dir = os.path.join(os.curdir, 'asset', 'data', 'duel.json')
    with open(duel_dir , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        return data_dict
    return None

async def write_duel_data(in_dict: dict) -> bool:
    duel_dir = os.path.join(os.curdir, 'asset', 'data', 'duel.json')
    with open(duel_dir , 'w', encoding='utf-8') as data_json:
        json.dump(in_dict, data_json, ensure_ascii = False)
        return True
    return False

async def add_single_duel(user_id: int, group_id: int, bullets_use: int, is_dead: bool):
    duel_data = await get_duel_data()
    if not str(group_id) in duel_data:
        duel_data[str(group_id)] = {}
    if not str(user_id) in duel_data[str(group_id)]:
        duel_data[str(group_id)][str(user_id)] = {}
    user_data = duel_data[str(group_id)][str(user_id)]
    if not str(bullets_use) in user_data:
        user_data[str(bullets_use)] = {}
    bullet_data = user_data[str(bullets_use)]
    if not 'death' in bullet_data:
        bullet_data['death'] = 0
    if not 'alive' in bullet_data:
        bullet_data['alive'] = 0
    if is_dead:
        bullet_data['death'] = bullet_data['death'] + 1
    else:
        bullet_data['alive'] = bullet_data['alive'] + 1
    user_data[str(bullets_use)] = bullet_data
    duel_data[str(group_id)][str(user_id)] = user_data
    result = await write_duel_data(duel_data)
    return result

async def get_user_duel_data(group_id: int, user_id: int, bullets_use: int = 0):
    duel_data = await get_duel_data()
    if not str(group_id) in duel_data:
        return None
    if not str(user_id) in duel_data[str(group_id)]:
        return None
    user_data = duel_data[str(group_id)][str(user_id)]
    if bullets_use == 0:
        r_data = {}
        for key in user_data:
            for s_key in user_data[key]:
                if not s_key in r_data:
                    r_data[s_key] = 0
                r_data[s_key] = r_data[s_key] + user_data[key][s_key]
        if not r_data:
            return None
        return r_data
    else:
        if not str(bullets_use) in user_data:
            return None
        else:
            return user_data[str(bullets_use)]
