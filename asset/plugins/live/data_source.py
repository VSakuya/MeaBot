import json
import os
import requests
from bs4 import BeautifulSoup
from urllib import request as req
from urllib.request import urlopen
import urllib.request
import urllib.parse

B_ROOM_NUM = 349991143
YB_CN_ID = 'UCWCc8tO-uUl_7SJXIKJACMw'
# YB_CN_ID = 'UCiZLTDFNOGtM3s76kbudaOQ'
# URL_YTB = 'https://www.youtube.com/results?search_query=UCWCc8tO-uUl_7SJXIKJACMw&sp=EgQQAUAB&pbj=1'
# URL_YTB = 'https://www.youtube.com/results?search_query=神楽めあ+/+KaguraMea&sp=EgQQAUAB&pbj=1'
# URL_YTB = 'https://www.youtube.com/results?search_query=UCiZLTDFNOGtM3s76kbudaOQ&sp=EgQQAUAB&pbj=1'
URL_YTB = 'https://www.youtube.com/channel/UCWCc8tO-uUl_7SJXIKJACMw'
# URL_YTB = 'https://www.youtube.com/channel/UCWCc8tO-uUl_7SJXIKJACMw/videos'
# URL_YTB = 'https://www.youtube.com/channel/UC1opHUrw8rvnsadT-iGp7Cg'
URL_TC = 'https://twitcasting.tv/kaguramea_vov'

def check_file():
    if not os.path.exists(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'live.json'):
        empty_dict = {'live_state': True, 'live_time': 0}
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'live.json' , 'w', encoding='utf-8') as data_json:
            json.dump(empty_dict, data_json, ensure_ascii = False)
            
    print('live file checked')

async def get_B_live_data():
    global B_ROOM_NUM
    get_url = 'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid=%d'%B_ROOM_NUM
    result = requests.get(get_url)
    if result.status_code == 200:
        try:
            json_data = result.json()['data']
            return json_data
        except Exception as e:
            print (e)
            return False
    else:
        return False

async def get_YB_live_data():
    #国内测试开关
    # return False
    global URL_YTB
    cookie_youtube = 'GPS=1;' \
                    'VISITOR_INFO1_LIVE=gQXoeXTOXq4;' \
                    'YSC=tj2AJQwbR_U;'

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
        'Cookie': cookie_youtube,
        'Connection': 'keep-alive',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    request_ytb = req.Request(url=URL_YTB,headers=header)
    response_ytb = None
    try:
        response_ytb = req.urlopen(request_ytb)
    except:
        return False
        print('YTB data gather failed.')
    html = response_ytb.read().decode('utf8')
    
    soup = BeautifulSoup(html,'html.parser')
    if(soup):
        print(str(soup).find('LIVE NOW') )
        if str(soup).find('LIVE NOW') == -1:
            return False
        else:
            return True
    # global URL_YTB
    # header = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
    #     'Cookie': 'YSC=u_rsZq8AcBo; VISITOR_INFO1_LIVE=rY3gnbUq6Ag; GPS=1; ST-1oqoxkb=itct=CDMQk3UYACITCPP-t4_Iw-ICFcNxKgod5zUKkSj0JA%3D%3D&csn=5_XvXLPvB8PjqQHn66iICQ',
    #     'Connection': 'keep-alive',
    #     'Accept-Language': 'en-US,en;q=0.5',
    #     'Referer': 'https://www.youtube.com/results?search_query=UCWCc8tO-uUl_7SJXIKJACMw&sp=EgIQAQ%253D%253D',
    #     'X-YouTube-Client-Name': '1',
    #     'X-YouTube-Client-Version': '2.20190529',
    #     'X-YouTube-Page-CL': '250544815',
    #     'X-YouTube-Page-Label': 'youtube.ytfe.desktop_20190528_3_RC2',
    #     'X-YouTube-STS': '18045',
    #     'X-YouTube-Utc-Offset': '480',
    #     'X-YouTube-Variants-Checksum': '7e46d96e46a45788f840d135c2cf4890'
    # }
    # result = requests.get(URL_YTB, headers=header)
    # if result.status_code == 200:
    #     try:
    #         json_data = result.json()
    #         data_dict = {}
    #         result_count = int(json_data[1]['response']['estimatedResults'])
    #         data_dict['count'] = result_count
    #         if result_count > 0:
    #             list_data = json_data[1]['response']['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
    #             live_first_data = list_data[0]['videoRenderer']
    #             live_data_dict = {}
    #             live_data_dict['title'] = live_first_data['title']['simpleText']
    #             live_data_dict['url'] = 'https://www.youtube.com/watch?v=' + live_first_data['videoId']
    #             live_data_dict['cover'] = live_first_data['thumbnail']['thumbnails'][0]['url']
    #             data_dict['content'] = live_data_dict
    #         # print(data_dict)
    #         return data_dict
    #     except Exception as e:
    #         print (e)
    #         return False
    # else: 
    #     return False
    
    # global YB_CN_ID
    # get_url = 'https://www.googleapis.com/youtube/v3/search?part=id&channelId='+ YB_CN_ID +'&eventType=live&type=video&key=' + api_key
    # result = requests.get(get_url)
    # if result.status_code == 200:
    #     try:
    #         json_data = result.json()
    #         return json_data
    #     except Exception as e:
    #         print (e)
    #         return False
    # else:
    #     api_key = 'AIzaSyDdhzoVnd2ZvVW677bnhZGS0cpEB8HyDkA'
    #     get_url = 'https://www.googleapis.com/youtube/v3/search?part=id&channelId='+ YB_CN_ID +'&eventType=live&type=video&key=' + api_key
    #     result = requests.get(get_url)
    #     if result.status_code == 200:
    #         try:
    #             json_data = result.json()
    #             return json_data
    #         except Exception as e:
    #             print (e)
    #             return False
    # return False

async def get_TC_live_data():
    global URL_TC
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
    user_referer = URL_TC
    headers = {'User-Agent': user_agent, 'Referer': user_referer}
    req = urllib.request.Request(URL_TC, headers=headers)
    html = None
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
    except:
        print('TC data gather failed.')
        return False

    soup = BeautifulSoup(html,'html.parser')
    if(soup):
        return_dict = {}
        return_dict['status'] = False
        return_dict['url'] = URL_TC
        return_dict['image'] = ''
        status_soup = soup.find('span',  {'class': 'tw-player-page__live-status--online'})
        if status_soup:
            if 'style' in status_soup.attrs and status_soup.attrs['style'] == 'display:none;':
                pass
            else:
                return_dict['status'] = True
                image_soup = soup.find('meta', {'property': 'og:image'})
                if image_soup:
                    return_dict['image'] = image_soup.attrs['content']
                return return_dict
        
example = {
    'status' : True,
    'image' : 'a.jpg',
    'url' :'.com'
}

async def write_live_data(in_dict: dict) -> bool:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'live.json' , 'w', encoding='utf-8') as data_json:
        json.dump(in_dict, data_json, ensure_ascii = False)
        return True
    return False

async def get_live_data() -> dict:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'live.json' , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        return data_dict
    return None

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

# def get_file_CQ_dir(name : str) -> str :
#     global SONGS_PATH
#     file_dir = ''
#     file_dir = 'music' + os.sep + name
#     # if(sysstr == "Windows"):
#     #     file_dir = 'file:///' + SONGS_PATH + os.sep + name
#     # else:
#     #     file_dir = 'file://' + SONGS_PATH + os.sep + name
#     return file_dir


# async def update_songs() -> bool:
#     global SONGS_PATH
#     files = os.listdir(SONGS_PATH)
#     temp_list = []
#     black_list = ['/', '\t', '\b', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '-', ' ', '黒羽翼堕天']
#     for file in files :
#         if not os.path.isdir(file):
#             temp_file = file
#             for bl_item in black_list: 
#                 temp_file = temp_file.replace(bl_item, '')
#             os.rename(SONGS_PATH + os.sep + file, SONGS_PATH + os.sep + temp_file)

#             temp_list.append(temp_file)
#     await write_sing_data(temp_list)

# async def search_songs(name : str) -> list:
#     files = await get_sing_data()
#     temp_list = []
#     for file in files :
#         if bool(re.findall(name, file, flags=re.IGNORECASE)):
#             temp_list.append(file)
# #     return temp_list

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
