import json
import os
from config import global_var
import urllib.request
import time

IMG_PATH = global_var.get_coolq_dir() + os.sep + 'data' + os.sep + 'image' + os.sep + 'reply'
SOUND_PATH = global_var.get_coolq_dir() + os.sep + 'data' + os.sep + 'record' + os.sep + 'sound'

def check_file():
    if not os.path.exists(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply.json'):
        empty_dict = {}
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply.json' , 'w', encoding='utf-8') as data_json:
            json.dump(empty_dict, data_json, ensure_ascii = False)
    
    if not os.path.exists(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'sound.json'):
        empty_list = []
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'sound.json' , 'w', encoding='utf-8') as data_json:
            json.dump(empty_list, data_json, ensure_ascii = False)

    if not os.path.exists(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply_temp.json'):
        empty_dict = {}
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply_temp.json' , 'w', encoding='utf-8') as data_json:
            json.dump(empty_dict, data_json, ensure_ascii = False)
            
    print('autoreply file checked')

#raw_message用于防止首字跟呼号重复被自动去除
#exp:'咩咩[CQ:image,file=9A1B9AA4C2A675F91370D5F9499C17EF.jpg]'
async def meassage_convert(in_message:list, raw_message:str):
    re_msg = []
    i= 0
    for item in in_message:
        msg_data = item['data']
        msg_type = item['type']
        if msg_type == 'text':
            if i == 0:
                new_str = ''
                if '[CQ:' in raw_message:
                    new_str = raw_message[0 : raw_message.find('[CQ:')]
                else:
                    new_str = raw_message
                item['data']['text'] = new_str
            re_msg.append(item)
        elif  msg_type == 'image':
            global IMG_PATH
            org_file_name = msg_data['file']
            org_file_url = msg_data['url']
            file_type = org_file_name[org_file_name.find('.') + 1:]
            time_stamp = round(int(time.time() * 1000))
            file_name = str(time_stamp) + '.' + file_type
            try:
                urllib.request.urlretrieve(org_file_url, IMG_PATH + os.sep + file_name)
            except:
                return False
            img_item = {}
            img_item['type'] = 'image'
            img_item['data'] = {'file': os.sep + 'reply' + os.sep + file_name}
            re_msg.append(img_item)
        i += 1
    return re_msg

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

async def get_reply_data() -> dict:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply.json' , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        return data_dict
    return None

async def write_reply_data(in_dict: dict) -> bool:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply.json' , 'w', encoding='utf-8') as data_json:
        json.dump(in_dict, data_json, ensure_ascii = False)
        return True
    return False

async def add_reply_data(group_id, key : str, message : dict, submit_user_id : int, checked_user_id : int):
    data_dict = None
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply.json' , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        if not group_id:
            if not 'all' in data_dict:
                data_dict['all'] = {}
            item = data_dict['all']
            new_content = {
            'message': message,
            'sumbit_user_id' : submit_user_id,
            'checked_user_id' : checked_user_id
            }
            item[str(key)] = new_content
            data_dict['all'] = item
        else:
            if not str(group_id) in data_dict:
                data_dict[str(group_id)] = {}
            item = data_dict[str(group_id)]
            new_content = {
            'message': message,
            'sumbit_user_id' : submit_user_id,
            'checked_user_id' : checked_user_id
            }
            item[str(key)] = new_content
            data_dict[str(group_id)] = item

    if not data_dict:
        return False
    if await write_reply_data(data_dict):
        return True
    return False

async def get_key_list() -> list:
    data_dict = await get_reply_data()
    data_keys = []
    for key in data_dict:
        for key_i in data_dict[key]:
            data_keys.append(key_i)
    return data_keys

async def get_key_t_list() -> list:
    data_dict = await get_reply_t_data()
    data_keys = []
    for key in data_dict:
        if not key == 'max_id':
            data_keys.append(data_dict[key]['key'])
    return data_keys

#临时目录

example = {
    'max_id': 0,
    'id': 
    {
        'key': '你好|你你',
        'message': '233',
        'group_id' : 23333333,
        'submit_user_id' : 2444444444,
        'time': 0
    }
}

async def get_reply_t_data(group_id : int = 0) -> dict:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply_temp.json' , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        if group_id:
            result_list = {}
            for key in data_dict:
                if key == 'max_id':
                    continue
                temp_dict = data_dict[key]
                if int(temp_dict['group_id']) == int(group_id):
                    result_list[key] = temp_dict
            return result_list
        return data_dict
    return None

async def write_reply_t_data(in_dict: dict) -> bool:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply_temp.json' , 'w', encoding='utf-8') as data_json:
        json.dump(in_dict, data_json, ensure_ascii = False)
        return True
    return False

async def add_reply_t_data(key : str, group_id : int, message : dict, submit_user_id : int):
    data_dict = None
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply_temp.json' , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        max_id = 0
        if 'max_id' in data_dict:
            max_id = data_dict['max_id']
        if max_id == 0:
            data_dict['max_id'] = 1
        else:
            data_dict['max_id'] = max_id + 1
        
        time_stamp = round(int(time.time() * 1000))
        content = {
            'key' : key,
            'group_id' : group_id,
            'message' : message,
            'submit_user_id' : submit_user_id,
            'time' : time_stamp
        }
        data_dict[str(max_id + 1)] = content

    if await write_reply_t_data(data_dict):
        return max_id + 1
    return False

async def del_reply_t_data(id):
    data_dict = None
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'autoreply_temp.json' , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        id = str(id)
        if not id in data_dict:
            return True
        del data_dict[id]
    if not data_dict:
        return False
    if await write_reply_t_data(data_dict):
        return True
    return False

async def update_sounds() -> bool:
    global SOUND_PATH
    files = os.listdir(SOUND_PATH)
    temp_list = []
    black_list = [' ']
    for file in files :
        if not os.path.isdir(file):
            temp_file = file
            for bl_item in black_list: 
                temp_file = temp_file.replace(bl_item, '')
            os.rename(SOUND_PATH + os.sep + file, SOUND_PATH + os.sep + temp_file)

            temp_list.append(temp_file)
    return await write_sound_data(temp_list)

async def write_sound_data(in_list: list) -> bool:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'sound.json' , 'w', encoding='utf-8') as data_json:
        json.dump(in_list, data_json, ensure_ascii = False)
        return True
    return False

async def get_sound_data() -> list:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'sound.json' , 'r', encoding='utf-8') as data_json:
        data_list = json.load(data_json)
        return data_list
    return None




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

