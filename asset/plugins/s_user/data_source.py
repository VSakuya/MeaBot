import json
import os
import asyncio
from functions import special_user

def check_file():
    check_keys = special_user.get_special_user_keys()
    if not os.path.exists(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'special_user.json'):
        empty_dict = {}
        for key in check_keys:
            if key == 'auto_reply_checker':
                empty_dict[key] = {}
                continue
            empty_dict[key] = []
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'special_user.json' , 'w', encoding='utf-8') as data_json:
            json.dump(empty_dict, data_json, ensure_ascii = False)
    else:
        loop = asyncio.get_event_loop()
        check_dict = loop.run_until_complete(special_user.get_special_user_data())
        for key in check_keys:
            if not key in check_dict:
                if key == 'auto_reply_checker':
                    check_dict[key] = {}
                    continue
                check_dict[key] = []
        result = loop.run_until_complete(special_user.write_special_user_data(check_dict))
        # loop.close()
        if not result:
            print('special user添加key发生错误！')

    if not os.path.exists(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'black_list.json'):
        empty_list = []
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'black_list.json' , 'w', encoding='utf-8') as data_json:
            json.dump(empty_list, data_json, ensure_ascii = False)
    print('s_user file checked')

# async def write_special_user_data(in_list: list) -> bool:
#     with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'special_user.json' , 'w', encoding='utf-8') as data_json:
#         json.dump(in_list, data_json, ensure_ascii = False)
#         return True
#     return False

# async def get_special_user_data() -> list:
#     with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'special_user.json' , 'r', encoding='utf-8') as data_json:
#         data_dict = json.load(data_json)
#         return data_dict
#     return None


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
