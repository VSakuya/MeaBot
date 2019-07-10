import json
import os
import re
import platform
from config import global_var

SONGS_PATH = global_var.get_coolq_dir() + os.sep + 'data' + os.sep + 'record' + os.sep + 'music'

def check_file():
    if not os.path.exists(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'sing.json'):
        empty_list = []
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'mute.json' , 'w', encoding='utf-8') as data_json:
            json.dump(empty_list, data_json, ensure_ascii = False)
            
    print('sing file checked')

def get_file_CQ_dir(name : str) -> str :
    global SONGS_PATH
    file_dir = ''
    file_dir = 'music' + os.sep + name
    # if(sysstr == "Windows"):
    #     file_dir = 'file:///' + SONGS_PATH + os.sep + name
    # else:
    #     file_dir = 'file://' + SONGS_PATH + os.sep + name
    return file_dir

async def get_sing_data() -> list:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'sing.json' , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        return data_dict
    return None

async def write_sing_data(in_list: list) -> bool:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'sing.json' , 'w', encoding='utf-8') as data_json:
        json.dump(in_list, data_json, ensure_ascii = False)
        return True
    return False

async def update_songs() -> bool:
    global SONGS_PATH
    files = os.listdir(SONGS_PATH)
    temp_list = []
    black_list = ['/', '\t', '\b', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '-', ' ', '黒羽翼堕天','・','♡','〜']
    for file in files :
        if not os.path.isdir(file):
            temp_file = file
            for bl_item in black_list: 
                temp_file = temp_file.replace(bl_item, '')
            os.rename(SONGS_PATH + os.sep + file, SONGS_PATH + os.sep + temp_file)

            temp_list.append(temp_file)
    return await write_sing_data(temp_list)

async def search_songs(name : str) -> list:
    files = await get_sing_data()
    temp_list = []
    for file in files :
        if bool(re.findall(name, file, flags=re.IGNORECASE)):
            temp_list.append(file)
    return temp_list

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
