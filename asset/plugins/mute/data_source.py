import json
import os
from functions import tools

DEF_REMOVE_MUTE_PERCENTAGE = 10

def check_file():
    if not os.path.exists(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'mute.json'):
        empty_list = []
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'mute.json' , 'w', encoding='utf-8') as data_json:
            json.dump(empty_list, data_json, ensure_ascii = False)

    if not os.path.exists(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'mute_analyze.json'):
        empty_dict = {}
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'mute_analyze.json' , 'w', encoding='utf-8') as data_json:
            json.dump(empty_dict, data_json, ensure_ascii = False)

    print('mute file checked')

async def arrange_data():
    org_list = await get_mute_data()
    temp_list = []

    for i in range(len(org_list)):
        item = org_list[i]
        if not temp_list:
            temp_list.append(item)
        is_match = False
        for j in range(len(temp_list)):
            temp_item = temp_list[j]
            if temp_item['user_id'] == item['user_id'] and temp_item['group_id'] == item['group_id'] and temp_item['mute_time'] == item['mute_time']:
                is_match = True
                if temp_item['key_word'] == item['key_word']:
                   pass
                else:
                    temp_item['key_word'] = temp_item['key_word'] + '|' + item['key_word']
        if not is_match:
            temp_list.append(item)
    await write_mute_data(temp_list)
                
async def del_data_by_index(index : int) -> bool:
    data_list = await get_mute_data()
    if index < 0 or index > len(data_list) - 1:
        return False
    del data_list[index]
    await write_mute_data(data_list)
    return True

async def get_mute_data() -> list:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'mute.json' , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        return data_dict
    return None

async def write_mute_data(in_list: list) -> bool:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'mute.json' , 'w', encoding='utf-8') as data_json:
        json.dump(in_list, data_json, ensure_ascii = False)
        return True
    return False

async def get_mute_analyze_data() -> dict:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'mute_analyze.json' , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        return data_dict
    return None

async def add_mute_analyze_time(sec: int, group_id: int):
    cur_ma_data = await get_mute_analyze_data()
    if not str(group_id) in cur_ma_data:
        cur_ma_data[str(group_id)] = {}
    group_data = cur_ma_data[str(group_id)]
    if not 'sum_this_day' in group_data:
        group_data['sum_this_day'] = sec
    else:
        group_data['sum_this_day'] = group_data['sum_this_day'] + sec

    if not 'sum_this_week' in group_data:
        group_data['sum_this_week'] = sec
    else:
        group_data['sum_this_week'] = group_data['sum_this_week'] + sec
    
    if not 'sum_this_month' in group_data:
        group_data['sum_this_month'] = sec
    else:
        group_data['sum_this_month'] = group_data['sum_this_month'] + sec
    
    result = await write_mute_analyze_data(cur_ma_data)
    return result

# return: 0:不刷新任何记录; 1: 刷新日最大; 2:刷新周最大; 3:刷新月最大；11:持平日；21：持平周；31：持平月
async def compare_mute_time(sec: int, user_id: int, group_id: int, nickname: str) -> int:
    cur_ma_data = await get_mute_analyze_data()
    if not str(group_id) in cur_ma_data:
        cur_ma_data[str(group_id)] = {}
    group_data = cur_ma_data[str(group_id)]
    if not 'max_cur_day' in group_data:
        group_data['max_cur_day'] = {}
    if not 'max_cur_week' in group_data:
        group_data['max_cur_week'] = {}
    if not 'max_cur_month' in group_data:
        group_data['max_cur_month'] = {}
    max_day_data = group_data['max_cur_day']
    max_week_data = group_data['max_cur_week']
    max_month_data = group_data['max_cur_month']
    result = 0
    if not max_day_data:
        max_day_data['sec'] = sec
        max_day_data['user_id'] = [user_id]
        max_day_data['nickname'] = [nickname]
    elif sec > max_day_data['sec']:
        max_day_data['sec'] = sec
        max_day_data['user_id'] = [user_id]
        max_day_data['nickname'] = [nickname]
        result = 1
    elif sec == max_day_data['sec']:
        max_day_data['sec'] = sec
        max_day_data['user_id'].append(user_id)
        max_day_data['nickname'].append(nickname)
        result = 11

    if not max_week_data:
        max_week_data['sec'] = sec
        max_week_data['user_id'] = [user_id]
        max_week_data['nickname'] = [nickname]
    elif sec > max_week_data['sec']:
        max_week_data['sec'] = sec
        max_week_data['user_id'] = [user_id]
        max_week_data['nickname'] = [nickname]
        result = 2
    elif sec == max_week_data['sec']:
        max_week_data['sec'] = sec
        max_week_data['user_id'].append(user_id)
        max_week_data['nickname'].append(nickname)
        result = 21
    
    if not max_month_data:
        max_month_data['sec'] = sec
        max_month_data['user_id'] = [user_id]
        max_month_data['nickname'] = [nickname]
    elif sec > max_month_data['sec']:
        max_month_data['sec'] = sec
        max_month_data['user_id'] = [user_id]
        max_month_data['nickname'] = [nickname]
        result = 3
    elif sec == max_month_data['sec']:
        max_month_data['sec'] = sec
        max_month_data['user_id'].append(user_id)
        max_month_data['nickname'].append(nickname)
        result = 31

    group_data['max_cur_day'] = max_day_data
    group_data['max_cur_week'] = max_week_data
    group_data['max_cur_month'] = max_month_data
    cur_ma_data[str(group_id)] = group_data
    await write_mute_analyze_data(cur_ma_data)
    return result


async def update_remove_percentage(group_id: int ,new_value: int):
    cur_ma_data = await get_mute_analyze_data()
    if not 'cur_remove_percentage' in cur_ma_data:
        cur_ma_data['cur_remove_percentage'] = {}
    cur_ma_data['cur_remove_percentage'][str(group_id)] = new_value
    result = await write_mute_analyze_data(cur_ma_data)
    return result

async def get_remove_percentage(group_id: int):
    cur_ma_data = await get_mute_analyze_data()
    global DEF_REMOVE_MUTE_PERCENTAGE
    if not 'cur_remove_percentage' in cur_ma_data or not str(group_id) in cur_ma_data['cur_remove_percentage']:
        return DEF_REMOVE_MUTE_PERCENTAGE
    return cur_ma_data['cur_remove_percentage'][str(group_id)]
    
async def reset_remove_percentage():
    cur_ma_data = await get_mute_analyze_data()
    global DEF_REMOVE_MUTE_PERCENTAGE
    if not 'cur_remove_percentage' in cur_ma_data:
        return True
    for key in cur_ma_data['cur_remove_percentage']:
        cur_ma_data['cur_remove_percentage'][key] = DEF_REMOVE_MUTE_PERCENTAGE
    result = await write_mute_analyze_data(cur_ma_data)
    return result


async def write_mute_analyze_data(in_dict: dict) -> bool:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'mute_analyze.json' , 'w', encoding='utf-8') as data_json:
        json.dump(in_dict, data_json, ensure_ascii = False)
        return True
    return False

async def add_mute_data(content : dict) -> bool:
    data_list = []
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'mute.json' , 'r', encoding='utf-8') as data_json:
        data_list = json.load(data_json)
    
    is_match = False
    for i in range(len(data_list)):
        item = data_list[i]
        if content['user_id'] == item['user_id'] and content['group_id'] == item['group_id'] and content['mute_time'] == item['mute_time']:
            is_match = True
            data_list[i]['key_word'] = content['key_word'] + '|' + item['key_word']
    if not is_match:
        data_list.append(content)
    if await write_mute_data(data_list):
        return True
    return False

# def is_int(s : str) -> bool:
#     try:
#         int(s)
#         return True
#     except ValueError:
#         pass
 
#     try:
#         import unicodedata
#         unicodedata.numeric(s)
#         return True
#     except (TypeError, ValueError):
#         pass
 
#     return False

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
