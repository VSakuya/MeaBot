import json
import os
import math

class black_list:
    @staticmethod
    async def get_black_list_data() -> list:
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'black_list.json' , 'r', encoding='utf-8') as data_json:
            data_list = json.load(data_json)
            return data_list
        return None

    @staticmethod
    async def write_black_list_data(in_list: list) -> bool:
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'black_list.json' , 'w', encoding='utf-8') as data_json:
            json.dump(in_list, data_json, ensure_ascii = False)
            return True
        return False

    @staticmethod
    async def add_black_list_data(user_id : int):
        data_list = []
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'black_list.json' , 'r', encoding='utf-8') as data_json:
            data_list = json.load(data_json)
            if not user_id in data_list:
                data_list.append(user_id)
            else:
                return True
        if not data_list:
            return False
        if await black_list.write_black_list_data(data_list):
            return True
        return False

    @staticmethod
    async def is_black_list(user_id : int):
        bl = await black_list.get_black_list_data()
        if user_id in bl:
            return True
        return False

class special_user:
    __su_keys = [
        'live_alert', 
        'alpha_test', 
        'sponsor',
        'auto_reply_checker'
    ]

    @staticmethod
    def get_special_user_keys() -> list:
        return special_user.__su_keys

    @staticmethod
    async def write_special_user_data(in_dict: dict) -> bool:
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'special_user.json' , 'w', encoding='utf-8') as data_json:
            json.dump(in_dict, data_json, ensure_ascii = False)
            return True
        return False

    @staticmethod
    async def get_special_user_data() -> dict:
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'special_user.json' , 'r', encoding='utf-8') as data_json:
            data_dict = json.load(data_json)
            return data_dict
        return None
    
    @staticmethod
    async def get_live_alert_list() -> list:
        su_dict = await special_user.get_special_user_data()
        return su_dict['live_alert']
    
    @staticmethod
    async def add_live_alert_user(new_id: int) -> bool:
        su_dict = await special_user.get_special_user_data()
        if su_dict:
            su_dict['live_alert'].append(new_id)
            result = await special_user.write_special_user_data(su_dict)
            return result
        return False
    
    @staticmethod
    async def get_alpha_test_list() -> list:
        su_dict = await special_user.get_special_user_data()
        return su_dict['alpha_test']
    
    @staticmethod
    async def add_alpha_test_user(new_id: int) -> bool:
        su_dict = await special_user.get_special_user_data()
        if su_dict:
            su_dict['alpha_test'].append(new_id)
            result = await special_user.write_special_user_data(su_dict)
            return result
        return False

    @staticmethod
    async def get_sponsor_list() -> list:
        su_dict = await special_user.get_special_user_data()
        return su_dict['sponsor']

    @staticmethod
    async def add_sponsor_user(new_id: int) -> bool:
        su_dict = await special_user.get_special_user_data()
        if su_dict:
            su_dict['sponsor'].append(new_id)
            result = await special_user.write_special_user_data(su_dict)
            return result
        return False

    #输入0返回所有列表内用户
    @staticmethod
    async def get_auto_reply_checker_data_by_group_id(id: int = 0) -> list:
        su_dict = await special_user.get_special_user_data()
        if id == 0:
            result_list = []
            temp_dict = su_dict['auto_reply_checker']
            for t_key in temp_dict:
                temp_list = temp_dict[t_key]
                for id in temp_list:
                    if not id in result_list:
                        result_list.append(id)
            return result_list
        if str(id) in su_dict['auto_reply_checker']:
            return su_dict['auto_reply_checker'][str(id)]

    @staticmethod
    async def get_auto_reply_checker_group_by_user_id(id: int) -> list:
        su_dict = await special_user.get_special_user_data()
        result_list = []
        for key in su_dict['auto_reply_checker']:
            if id in su_dict['auto_reply_checker'][key]:
                result_list.append(int(key))
        return result_list

    @staticmethod
    async def get_auto_reply_checker_data() -> dict:
        su_dict = await special_user.get_special_user_data()
        return su_dict['auto_reply_checker']

    @staticmethod
    async def add_auto_reply_checker_user(new_id: int, group_id: int) -> bool:
        su_dict = await special_user.get_special_user_data()
        if su_dict:
            rc_data = su_dict['auto_reply_checker']
            if not str(group_id) in rc_data:
                rc_data[str(group_id)] = []
            if not new_id in rc_data[str(group_id)]:
                rc_data[str(group_id)].append(new_id)
            result = await special_user.write_special_user_data(su_dict)
            return result
        return False

    @staticmethod
    async def get_allowed_friend_list() -> list:
        data_dict = await special_user.get_special_user_data()
        if data_dict:
            result_list = []
            for key in data_dict:
                if type(data_dict[key]) == list:
                    temp_list = data_dict[key]
                    for id in temp_list:
                        if not id in result_list:
                            result_list.append(id)
                elif type(data_dict[key]) == dict:
                    temp_dict = data_dict[key]
                    for t_key in temp_dict:
                        temp_list = temp_dict[t_key]
                        for id in temp_list:
                            if not id in result_list:
                                result_list.append(id)
            return result_list

class tools:
    @staticmethod
    def sec_to_str(sec: int) -> str:
        minute = math.floor(sec / 60)
        hours = math.floor(minute / 60)
        days = math.floor(hours / 24)
        hours = hours - days * 24
        minute = minute - hours * 60 - days * 24 * 60
        r_str = ''
        if days > 0:
            r_str = r_str + '%d天'%days
        if hours > 0:
            r_str = r_str + '%d小时'%hours
        if minute > 0:
            r_str = r_str + '%d分钟'%minute
        return r_str

    @staticmethod
    def is_int(s : str) -> bool:
        try:
            int(s)
            return True
        except ValueError:
            pass
    
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
    
        return False