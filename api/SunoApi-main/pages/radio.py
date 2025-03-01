# -*- coding:utf-8 -*-

import streamlit as st
import time,json,os,ast
from datetime import timezone
import dateutil.parser

from streamlit_option_menu import option_menu
from streamlit_modal import Modal
import streamlit.components.v1 as components
import streamlit_antd_components as sac

root_dir = os.path.dirname(os.path.realpath(__file__))
# print(root_dir)
import sys
sys.path.append(root_dir)
import site
site.addsitedir(root_dir)
from streamlit_image_select import image_select

from utils import get_similar,get_feed,local_time
from cookie import get_random_token

from sqlite import SqliteTool

suno_sqlite = SqliteTool()

st.set_page_config(page_title="SunoAPI AI Music Generator",
                   page_icon="🎵",
                   layout="wide",
                   initial_sidebar_state="collapsed",
                   menu_items={
                       'Report a bug': "https://github.com/SunoApi/SunoApi/issues",
                       'About': "SunoAPI AI Music Generator is a free AI music generation software, calling the existing API interface to achieve AI music generation. If you have any questions, please visit our website url address: https://sunoapi.net\n\nDisclaimer: Users voluntarily input their account information that has not been recharged to generate music. Each account can generate five songs for free every day, and we will not use them for other purposes. Please rest assured to use them! If there are 10000 users, the system can generate 50000 songs for free every day. Please try to save usage, as each account can only generate five songs for free every day. If everyone generates more than five songs per day, it is still not enough. The ultimate goal is to keep them available for free generation at any time when needed.\n\n"
                   })

hide_streamlit_style = """
<style>#root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 5rem;}</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

i18n_dir = os.path.join(root_dir, "../i18n")
# print(i18n_dir)

def load_locales():
    locales = {}
    for root, dirs, files in os.walk(i18n_dir):
        for file in files:
            if file.endswith(".json"):
                lang = file.split(".")[0]
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    locales[lang] = json.loads(f.read())
    return locales

locales = load_locales()
display_languages = []

if 'Language' not in st.session_state:
    st.session_state.selected_index = 7
    st.session_state.Language = "ZH"


for i, code in enumerate(locales.keys()):
    display_languages.append(f"{code} - {locales[code].get('Language')}")
    if code == st.session_state.Language:
        st.session_state.selected_index = i
        st.session_state.Language = code

def change_language():
    # print("st.session_state.selectbox_value:" + st.session_state.selectbox_value)
    for item in display_languages:
        if item == st.session_state.selectbox_value:
            # print("item:" + item)
            st.session_state.selected_index = display_languages.index(item)
            st.session_state.Language = item.split(" - ")[0]
    # print("st.session_state.selected_index:" + str(st.session_state.selected_index))

col1, col2, col3 = st.columns(3)

# col2.selectbox(label="Language", options=display_languages, label_visibility='collapsed',index=st.session_state.selected_index, key="selectbox_value", on_change=change_language)

def i18n(key):
    loc = locales.get(st.session_state.Language, {})
    return loc.get("Translation", {}).get(key, key)

st.session_state['disabled_state'] = False
st.session_state['prompt_input'] = ""
st.session_state['tags_input'] = ""
st.session_state['title_input'] = ""
st.session_state["continue_at"] = ""
st.session_state["continue_clip_id"] = ""
st.session_state.DescPrompt = ""

with st.sidebar:
    selected = option_menu(None, [i18n("Music Song Create"), i18n("Music Share Square"), i18n("Music Project Readme"),i18n("Visit Official WebSite")], icons=['music-note', 'music-note-beamed', 'music-note-list'], menu_icon="cast", default_index=3)
    
    if selected == i18n("Music Song Create"):
        st.switch_page("main.py")
    elif selected == i18n("Music Share Square"):
        st.switch_page("pages/square.py")
    elif selected == i18n("Music Project Readme"):
        st.switch_page("pages/readme.py")
    elif selected == i18n("Visit Official WebSite"):
        st.page_link("https://suno.com", label=i18n("Visit Official WebSite1"), icon="🌐")
        st.page_link("https://sunoapi.net", label=i18n("Visit Official WebSite2"), icon="🌐")
    # print(selected)

st.sidebar.image('https://sunoapi.net/images/wechat.jpg', caption=i18n("Join WeChat Group"))
# st.sidebar.image('https://sunoapi.net/images/donate.jpg', caption=i18n("Buy me a Coffee"))
st.sidebar.markdown(f'<div data-testid="stImageCaption" class="st-emotion-cache-1b0udgb e115fcil0" style="max-width: 100%;"> {i18n("Friendly Link")}</div>', unsafe_allow_html=True)
result = suno_sqlite.query_many("select link,label,status from link where status=0 order by id")
# print(result)
# print("\n")
if result is not None and len(result) > 0:
    for row in result:
        st.sidebar.page_link(row[0], label=row[1], icon="🌐")

def change_page():
    st.session_state["click_image"] = False
    # print("st.session_state.change_page:" + str(st.session_state.change_page))
    st.session_state.page = 1 if 'change_page' not in st.session_state else st.session_state.change_page

if 'page' not in st.session_state:
    st.session_state.page = 1
# print(st.session_state["page"])

aid = ""
if 'aid' in st.session_state and len(st.session_state.aid) == 36:
    aid = st.session_state.aid
    # print(aid)
else:
    if 'aid' not in st.session_state and len(st.query_params.get_all("id")) == 0:
        # col2.error(i18n("FetchFeed FeedID Error"))
        st.switch_page("pages/square.py")
    elif st.query_params.id != "" and len(st.query_params.id) == 36:
        aid = st.query_params["id"]

result = get_similar(aid, 40, get_random_token())
# print(result)
# print("\n")


def localdatetime(str):
    # 将字符串时间 转化为 datetime 对象
    dateObject = dateutil.parser.isoparse(str)
    # print(dateObject)  2021-09-03 20:56:35.450686+00:00
    # from zoneinfo import ZoneInfo
    # 根据时区 转化为 datetime 数据
    # localdt = dateObject.replace(tzinfo = timezone.utc).astimezone(ZoneInfo("Asia/Shanghai"))
    localdt = dateObject.replace(tzinfo = timezone.utc).astimezone(tz=None)
    # print(localdt)  # 2021-09-04 04:56:35.450686+08:00
    # 产生本地格式 字符串
    # print(localdt.strftime('%Y-%m-%d %H:%M:%S'))
    return localdt.strftime('%Y-%m-%d %H:%M:%S')


titles = []
images = []
captions = []
if result is not None and len(result) > 0 and 'similar_clips' in result:
    for data in result['similar_clips']:
        # print(data)
        # print("\n")
        title = ""
        title += i18n("FeedID") + ("None\n" if data['id'] is None or "" else data['id'] + "\n")
        title += i18n("Title") + ("None\n" if data['title'] is None or "" else data['title'] + "\n")
        title += i18n("Desc Prompt") + ("None\n" if data['metadata']['gpt_description_prompt'] is None or "" else data['metadata']['gpt_description_prompt'] + "\n")
        title += i18n("Tags") + ("None\n" if data['metadata']['tags'] is None or "" else data['metadata']['tags'] + "  " + i18n("Music Duration")  + ("None\n" if data['metadata']['duration'] is None or "" else str(int(data['metadata']['duration']/60)) + ":" + str("00" if int(data['metadata']['duration']%60) == 0 else ("0" + str(int(data['metadata']['duration']%60))  if int(data['metadata']['duration']%60) <10 else int(data['metadata']['duration']%60))) + " \n"))
        title += i18n("Music Created At")  + ("None\n" if data['created_at'] is None or "" else localdatetime(data['created_at'])) + "  " +  i18n("Select Model") +  ("None\n" if data['model_name'] is None or "" else data['model_name'] + "\n\n")
        title += i18n("Music Prompt")  + ("None\n" if data['metadata']['prompt'] is None or "" else data['metadata']['prompt'] + "\n")
        
        titles.append(title)
        captions.append("sunoai" if data['title'] is None or "" else f'<div style="justify-content: center; align-items: center; word-break: break-word; text-align: center;padding-right: 15px;">{data["title"]}</div>')
        images.append("https://sunoapi.net/images/sunoai.jpg" if data['image_url'] is None or "" else data['image_url'])

print("\n")

index = 0
use_container_width = False

if 'index' not in st.session_state:
    st.session_state.index = -1
if 'click_image' not in st.session_state:
    st.session_state["click_image"] = False

if len(images) > 0 and len(images)%40 == 0:
    use_container_width = True
    
index = image_select(
            label="",
            images=images if len(images) > 0 else ["https://sunoapi.net/images/sunoai.jpg"],
            captions=captions if len(captions) > 0 else [i18n("No Search Result")],
            titles=titles if len(titles) > 0 else [""],
            use_container_width=use_container_width,
            return_value="index"
        )

open_modal = True

if 'index' not in st.session_state:
    open_modal = False
elif 'index' in st.session_state and st.session_state.index != index:
    open_modal = True
else:
    open_modal = False

st.session_state.index = index

data = {}

if result is not None and len(result) > 0 and 'similar_clips' in result:
    data = result['similar_clips'][index]
    # video_modal = Modal(title=data['title'], key="video_modal", padding=20, max_width=520)

# if result and open_modal:
#     video_modal.open()

# if result and video_modal.is_open():
#     with video_modal.container():
#         if data['status'] == "complete":
#             st.session_state.index = index
#             st.video(data['video_url'])
#         else:
#             st.error(i18n("Generation Task Status") + data["status"])

# print(index)
# print(st.session_state["click_image"])


def get_music_feed(aid, token):
    resp = get_feed(aid.strip(), token)
    # print(resp)
    # print("\n")
    status = resp["detail"] if "detail" in resp else resp[0]["status"]
    if status != "Unauthorized" and status != "Not found." and status != "error" and "refused" not in status:
        result = suno_sqlite.query_one("select aid from music where aid =?", (aid.strip(),))
        # print(result)
        # print("\n")
        if result:
            # result = suno_sqlite.operate_one("update music set data=?, updated=(datetime('now', 'localtime')), sid=?, name=?, image=?, title=?, tags=?, prompt=?, duration=?, status=? where aid =?", (str(resp[0]), resp[0]["user_id"], resp[0]["display_name"], resp[0]["image_url"], resp[0]["title"], resp[0]["metadata"]["tags"], resp[0]["metadata"]["gpt_description_prompt"], resp[0]["metadata"]["duration"], resp[0]["status"], aid.strip()))
            # print(local_time() + " " + resp[0]["id"] + " update success")
            pass
        else:
            result = suno_sqlite.operate_one("insert into music (aid, data, sid, name, image, title, tags, prompt,duration, created, updated, status, private) values(?,?,?,?,?,?,?,?,?,?,?,?,?)", (str(resp[0]["id"]), str(resp[0]), resp[0]["user_id"], resp[0]["display_name"], resp[0]["image_url"], resp[0]["title"], resp[0]["metadata"]["tags"], resp[0]["metadata"]["gpt_description_prompt"], resp[0]["metadata"]["duration"],localdatetime(resp[0]['created_at']),localdatetime(resp[0]['created_at']), resp[0]["status"], 0))
            print(local_time() + " " + resp[0]["id"] + " insert success")
        # print(result)
        # print("\n")
        if status == "complete":
            pass
            # print(local_time() + " " + resp[0]["id"] + " complete success")
        else:
            print(local_time() + " " + (status if "metadata" not in resp else resp[0]['metadata']["error_message"]))
    else:
        print(local_time() + " " + (status if "metadata" not in resp else resp[0]['metadata']["error_message"]))

if st.session_state["click_image"] == False:
    st.session_state["click_image"] = True
elif 'change_page' in st.session_state and index == 0:
    st.session_state["click_image"] = True
else:
    # print(data['id'])
    get_music_feed(data['id'], get_random_token())
    st.session_state.aid = data['id']
    # print(st.session_state.aid)
    st.switch_page("pages/song.py")

# print(index)
# print(st.session_state["click_image"])

# 隐藏右边的菜单以及页脚
hide_streamlit_style = """
<style>
#MainMenu {display: none;}
footer {display: none;}
.eczjsme10 {display: none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Artalk评论初始化
hide_streamlit_style1 = f"""
<!-- CSS -->
<link href="https://sunoapi.net/dist/Artalk.css" rel="stylesheet" />
<!-- JS -->
<script src="https://sunoapi.net/dist/Artalk.js"></script>
<!-- Artalk -->
<div style="font-size: 12px;font-family: inherit; color: #697182;justify-content: center; align-items: center; word-break: break-word; text-align: center;padding-right: 15px;">本页浏览量 <span id="ArtalkPV">Loading...</span> 次</div>
<div id="Comments"></div>
<script>
Artalk.init({{
el:        '#Comments',
pageKey:   '/radio',
pageTitle: '音乐类似歌曲',
server:    'https://sunoapi.net',
site:      'SunoAPI AI Music Generator',
}})
</script>
"""
components.html(hide_streamlit_style1, height=0)

components.iframe("https://sunoapi.net/analytics.html", height=0)