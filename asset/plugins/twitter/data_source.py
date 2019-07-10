from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4 import element
import json
import os
import urllib.request
import urllib.parse

TWITTER_URL = 'https://twitter.com/KaguraMea_VoV'
# TWITTER_URL = 'https://twitter.com/VSakuya'

def check_file():
    if not os.path.exists(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'twitter.json'):
        empty_dict = {}
        with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'twitter.json' , 'w', encoding='utf-8') as data_json:
            json.dump(empty_dict, data_json, ensure_ascii = False)
    
    print('twitter file checked')

async def get_html_soup(url : str):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
    user_referer = url
    headers = {'User-Agent': user_agent, 'Referer': user_referer}
    req = urllib.request.Request(url, headers=headers)
    html = None
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
    except:
        print(url + ' get failed.')
        return False
    soup = BeautifulSoup(html,'html.parser')
    return soup

async def pull_twitter_data() -> dict:
    # 国内测试开关
    # return False
    org_soup = await get_html_soup(TWITTER_URL)
    if not org_soup:
        return False
    main_con = org_soup.find('ol', id='stream-items-id')

    twitter_dict = {}
    con_list = main_con.find_all('div', {'class': 'js-stream-tweet'})
    for item in con_list:
        is_pinned = item.find('div', {'class': 'pinned'})
        if not is_pinned:
            single_dict = {}
            single_soup = item.find('div', {'class': 'content'})
            time = single_soup.find('span', {'class': '_timestamp'}).attrs['data-time']
            # print(time)
            text_soup = single_soup.find('p', {'class': 'TweetTextSize'})
            img_soup = single_soup.find_all('div', {'class': 'AdaptiveMedia-photoContainer'})
            # print(img_soup)
            img_urls = []
            if img_soup:
                for item in img_soup:
                    img_urls_soup = item.find('img')
                    img_urls.append(img_urls_soup.attrs['src'])
                # print(img_urls)
            if img_urls:
                single_dict['image'] = img_urls

            single_str = ''
            for s_item in text_soup:
                # print(s_item)
                # print(type(s_item))
                if(isinstance(s_item, element.Tag)):
                    if s_item.name == 'img':
                        single_str = single_str + s_item.attrs['alt']
                        # print(s_item.attrs['alt'])
                    elif s_item.name == 'a':
                        if 'twitter-timeline-link' in s_item['class'] and not 'u-hidden' in s_item['class']:
                            # print(s_item.attrs['data-expanded-url'])
                            single_str = single_str + s_item.attrs['data-expanded-url']
                        elif 'twitter-hashtag' in s_item['class']:
                            # print(s_item.find('b').string)
                            single_str = single_str + '#' + s_item.find('b').string
                        
                else:
                    single_str = single_str + s_item.string
                    # print(s_item)
                    # print('NO')
            # print (single_str)
            single_dict['text'] = single_str
            twitter_dict[time] = single_dict
    # print(twitter_dict)
    return twitter_dict

example = {
    '11:04 PM - 23 May 2019': {'text': '2233', 'image':[]}
}
# async def get_B_live_data():
#     global B_ROOM_NUM
#     get_url = 'https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid=%d'%B_ROOM_NUM
#     result = requests.get(get_url)
#     if result.status_code == 200:
#         try:
#             json_data = result.json()['data']
#             return json_data
#         except Exception as e:
#             print (e)
#             return False
#     else:
#         return False

async def write_twitter_data(in_dict: dict) -> bool:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'twitter.json' , 'w', encoding='utf-8') as data_json:
        json.dump(in_dict, data_json, ensure_ascii = False)
        return True
    return False

async def get_twitter_data() -> dict:
    with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'twitter.json' , 'r', encoding='utf-8') as data_json:
        data_dict = json.load(data_json)
        return data_dict
    return None

# async def write_live_alert_list_data(in_list: list) -> bool:
#     with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'live_alert_list.json' , 'w', encoding='utf-8') as data_json:
#         json.dump(in_list, data_json, ensure_ascii = False)
#         return True
#     return False

# async def get_live_alert_list_data() -> list:
#     with open(os.getcwd() + os.sep + 'asset' + os.sep + 'data' + os.sep +'live_alert_list.json' , 'r', encoding='utf-8') as data_json:
#         data_dict = json.load(data_json)
#         return data_dict
#     return None

# # def get_file_CQ_dir(name : str) -> str :
# #     global SONGS_PATH
# #     file_dir = ''
# #     file_dir = 'music' + os.sep + name
# #     # if(sysstr == "Windows"):
# #     #     file_dir = 'file:///' + SONGS_PATH + os.sep + name
# #     # else:
# #     #     file_dir = 'file://' + SONGS_PATH + os.sep + name
# #     return file_dir


# # async def update_songs() -> bool:
# #     global SONGS_PATH
# #     files = os.listdir(SONGS_PATH)
# #     temp_list = []
# #     black_list = ['/', '\t', '\b', '@', '#', '$', '%', '^', '&', '*', '(', ')', '[', ']', '-', ' ', '黒羽翼堕天']
# #     for file in files :
# #         if not os.path.isdir(file):
# #             temp_file = file
# #             for bl_item in black_list: 
# #                 temp_file = temp_file.replace(bl_item, '')
# #             os.rename(SONGS_PATH + os.sep + file, SONGS_PATH + os.sep + temp_file)

# #             temp_list.append(temp_file)
# #     await write_sing_data(temp_list)

# # async def search_songs(name : str) -> list:
# #     files = await get_sing_data()
# #     temp_list = []
# #     for file in files :
# #         if bool(re.findall(name, file, flags=re.IGNORECASE)):
# #             temp_list.append(file)
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
