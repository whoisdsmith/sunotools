<div align="center">

[简体中文](https://github.com/SunoApi/SunoApi/blob/main/README_ZH.md) | [Русский](https://github.com/SunoApi/SunoApi/blob/main/README_RU.md) | [English](https://github.com/SunoApi/SunoApi/blob/main/README.md) | [한국어](https://github.com/SunoApi/SunoApi/blob/main/README_KR.md) | [日本語](https://github.com/SunoApi/SunoApi/blob/main/README_JP.md) | [Français](https://github.com/SunoApi/SunoApi/blob/main/README_FR.md) | [Deutsch](https://github.com/SunoApi/SunoApi/blob/main/README_DE.md)


[![GitHub release](https://img.shields.io/github/v/release/SunoApi/SunoApi?label=release&color=black)](https://img.shields.io/github/v/release/SunoApi/SunoApi?label=release&color=blue)  ![GitHub last commit](https://img.shields.io/github/last-commit/SunoApi/SunoApi)  ![GitHub commit activity](https://img.shields.io/github/commit-activity/t/SunoApi/SunoApi)  ![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/SunoApi/SunoApi)  ![SunoApi GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/SunoApi/SunoApi/total)  [![License](https://img.shields.io/badge/license-MIT-4EB1BA.svg)](https://www.apache.org/licenses/LICENSE-2.0.html)

# SunoAPI 非官方 Suno AI 用戶端

# 祝賀本開源項目入選本周weekly
### [![ruanyf](https://avatars.githubusercontent.com/u/905434?s=20) ruanyf added the weekly label 12 hours ago](https://github.com/ruanyf/weekly/issues/4263)

</div>



### 介紹

- 這是一個基於Python、Streamlit的非官方Suno API用戶端，現時支持生成音樂，獲取音樂資訊等功能。自帶維護token與保活功能，無需擔心token過期問題，可以設定多個帳號的資訊保存以便使用。

- GitHub有時候訪問不到，如無法訪問請移步Gitee地址： https://gitee.com/SunoApi/SunoApi

### 特點

- 填寫帳號資訊程式自動維護與保活
- 可以設定多個帳號的資訊保存使用
- 音樂分享廣場展示所有公開的歌曲
- 輸入音樂編號可直接獲取歌曲資訊
- 支援上傳圖片解析的內容生成歌曲
- 支援中文英文韓語日語等多國語言

### 調試

#### Python本地調試運行

- 尅隆源碼

```bash
git clone https://github.com/SunoApi/SunoApi.git
```

- 安裝依賴

```bash
cd SunoApi
pip3 install -r requirements.txt
```

- .env環境變數檔案，圖片識別需要用到gpt-4o的模型可以使用OpenAI的介面，也可以用其他的你自己常用的介面替換。 注册console.bitiful.com對象存儲帳號獲取S3_ACCESSKEY_ID，S3_SECRETKEY_ID參數用於圖片上傳到你創建的存儲桶，S3_WEB_SITE_URL填寫你的對象存儲帳號創建存儲桶後的外部訪問功能變數名稱。 這樣本地環境就可以測試圖片識別了。

```bash
OPENAI_BASE_URL = https://chatplusapi.cn
OPENAI_API_KEY = sk-xxxxxxxxxxxxxxxxxxxx
#S3_WEB_SITE_URL = https://cdn1.suno.ai
#S3_WEB_SITE_URL = http://localhost:8501
#S3_WEB_SITE_URL = http://123.45.67.8:8501
#S3_WEB_SITE_URL = https://sunoapi.s3.bitiful.net
S3_WEB_SITE_URL = https://res.sunoapi.net
S3_ACCESSKEY_ID = xxxxxxxxxxxxxxxxxxxx
S3_SECRETKEY_ID = xxxxxxxxxxxxxxxxxxxx
```


- 啟動項目，關於Streamlit請自行參攷Streamlit檔案

```bash
streamlit run main.py --server.maxUploadSize=3
```

### 部署

#### Docker 本地一鍵部署

```bash
docker run -d \
  --name sunoapi \
  --restart always \
  -p 8501:8501 \
  -v ./sunoapi.db:/app/sunoapi.db \
  -v ./images/upload:/app/images/upload \
  -v ./audios/upload:/app/audios/upload \
  -e OPENAI_BASE_URL=https://api.openai.com  \
  -e OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx \
  -e S3_WEB_SITE_URL=https://sunoapi.s3.bitiful.net  \
  -e S3_ACCESSKEY_ID=xxxxxxxxxxxxxxxxxxxx  \
  -e S3_SECRETKEY_ID=xxxxxxxxxxxxxxxxxxxx  \
  sunoapi/sunoapi:latest
```

##### 注意：需要把 https://sunoapi.s3.bitiful.net 替換成你自己的對象存儲桶的外部訪問功能變數名稱，最終上傳的圖片檔案能通過 http://xxxxxx.s3.bitiful.net/images/upload/xxxxxx.jpg 的形式能訪問到，不然OpenAI訪問不到這個你上傳的圖片就無法識別圖片內容，那麼上傳圖片生成音樂的功能將無法使用。


#### Docker 本地編譯部署

```bash
docker compose build && docker compose up
```

#### Dockerfile

```docker
FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 8501
CMD [ "nohup", "streamlit", "run", "main.py", "--server.maxUploadSize=3" ]
```

#### Docker 拉取鏡像部署

```bash
docker-compose pull && docker-compose up -d
```

#### docker-compose.yml

```docker
version: '3.2'

services:
  sunoapi:
    image: sunoapi/sunoapi:latest
    container_name: sunoapi
    ports:
      - "8501:8501"
    volumes:
      - ./sunoapi.db:/app/sunoapi.db
      - ./images/upload:/app/images/upload
      - ./audios/upload:/app/audios/upload
    environment:
      - TZ=Asia/Shanghai
      - OPENAI_BASE_URL=https://api.openai.com
      - OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
      - S3_WEB_SITE_URL=https://sunoapi.s3.bitiful.net
      - S3_ACCESSKEY_ID=xxxxxxxxxxxxxxxxxxxx
      - S3_SECRETKEY_ID=xxxxxxxxxxxxxxxxxxxx
    restart: always
```

##### 注意：拉取鏡像部署需要把項目裡面的sunoapi.db下載傳到你的docker-compose.yml檔案目錄，不然docker啟動會提示掛載不到檔案。

#### Streamlit 遠程倉庫部署

- 先Fork一份SunoApi程式碼到你的Github倉庫裡面
- 選擇Github授權登入： https://share.streamlit.io/
- 打開部署頁面： https://share.streamlit.io/deploy
- Repository選擇：SunoApi/SunoApi
- Branch輸入：main
- Main file path輸入：main.py
- 點擊Deploy！

#### Zeabur 一鍵部署

[![Deploy on Zeabur](https://zeabur.com/button.svg)](https://zeabur.com/templates/ORTEGG)

### 配寘

- 先從瀏覽器頁面登入狀態下中獲取自己的session和cookie。

- <a href="https://sunoapi.net" target="_blank"><img src="https://sunoapi.net/images/session.png" style="max-width: 100%;"/></a>

- 填寫設定資訊裡面後面會自動保活，可以填寫多個帳號資訊。

- <a href="https://sunoapi.net" target="_blank"><img src="https://sunoapi.net/images/session1.png" style="max-width: 100%;"/></a>

- 填寫後保存資訊，輸入identity可以更改修改帳號資訊。

- <a href="https://sunoapi.net" target="_blank"><img src="https://sunoapi.net/images/session2.png" style="max-width: 100%;"/></a>

### 完成

- 啟動運行項目後瀏覽器訪問 http://localhost:8501/ 即可使用了。

- <a href="https://sunoapi.net" target="_blank"><img src="https://sunoapi.net/images/index.png" style="max-width: 100%;"/></a>

- <a href="https://sunoapi.net" target="_blank"><img src="https://sunoapi.net/images/index1.png" style="max-width: 100%;"/></a>

- <a href="https://sunoapi.net" target="_blank"><img src="https://sunoapi.net/images/index2.png" style="max-width: 100%;"/></a>

- <a href="https://sunoapi.net" target="_blank"><img src="https://sunoapi.net/images/index3.png" style="max-width: 100%;"/></a>


### 問題

- 如果頁面提示資訊：請先設定資訊保存，然後再刷新頁面才能正常使用！ 請先添加自己的帳號資訊保存，然後把sunoapi.db資料庫裡面其他無效的帳號資訊删除，其中包括我測試的帳號資訊，然後再就可以正常使用了。
- 如果頁面提示資訊：Suno AI音樂歌曲生成提交失敗：Unauthorized.表示帳號登入狀態未授權，這種情況一般是多個瀏覽器用戶端登入了帳號形成了搶佔，退出其他登入的瀏覽器用戶端，保持帳號在這個Suno API AI音樂歌曲生成器用戶端登入，不要在其他瀏覽器用戶端登入就可以了。
- 如果頁面提示資訊：Suno AI音樂歌曲生成提交失敗：Insufficient credits.表示帳號資訊credits點數不足，請先添加自己的帳號資訊保存，然後再就可以正常使用了。
- 如果頁面提示出錯：ModuleNotFoundError: No module named 'streamlit_image_select'這是因為二次開發了一個streamlit_image_select組件的功能，二次開發後這個組件放在程式運行的pages目錄裡面，在程式運行目錄第一次加載streamlit_image_select組件是到Python3的site-packages目錄加載的，但是二次開發了的組件不能直接用pip3 install streamlit_image_select位置保存的程式，不然二次開發的功能無法使用，解決辦法就是點下左邊選單其他頁面連結後就可以正常加載使用了。
- 音樂生成任務提交成功後拉取生成任務隊列狀態，當狀態為“complete”時成功返回，這個時候默認停留了15秒等待官方生成檔案。 官方介面服務直接返回了媒體檔案Url地址，大部分時候頁面能正常顯示這些媒體檔案。 偶爾有時候介面已經返回了媒體檔案Url地址，但是實際檔案還不能從Url地址訪問到要等一會。 這個時候媒體檔案在頁面就可能無法加載到，可以點下媒體播放機滑鼠右鍵複製媒體檔案地址，用瀏覽器單獨打開這個地址就可以訪問到了或者直接右鍵另存為下載保存。或者到音樂分享廣場頁面清單裡面去查看生成的記錄。
- 關於設定帳號session和cookie資訊保存安全性問題，只要你的帳號不充值就沒必要擔心，因為不知道你的帳號密碼，你填寫的session和cookie資訊只要你的帳號在其他地方登入活動，或者在官方網站退出登入，那麼填寫的session和cookie就無效了，並且下次登入官網session和cookie都會發生變化的。


### 創作

- 專業歌詞輔助工具： https://poe.com/SuperSunoMaster


### 交流

- Github Issues： https://github.com/SunoApi/SunoApi/issues

<a href="https://sunoapi.net" target="_blank"><img src="https://sunoapi.net/images/wechat.jpg?20240923" style="max-width: 100%;"/></a>


### 參與

- 個人的力量始終有限，任何形式的貢獻都是歡迎的，包括但不限於貢獻程式碼，優化檔案，提交Issue和PR，由於時間有限不接受在微信或者微信群給開發者提Bug，有問題或者優化建議請提交Issue和PR！

<a href="https://star-history.com/#SunoApi/SunoApi" target="_blank"><img src="https://api.star-history.com/svg?repos=SunoApi/SunoApi" style="max-width: 100%;"/></a>


### 參攷

- Suno AI 官網: [https://suno.com](https://suno.com)
- Suno-API: [https://github.com/SunoAI-API/Suno-API](https://github.com/SunoAI-API/Suno-API)


### 聲明

- SunoAPI是一個非官方的開源項目，僅供學習和研究使用。用戶自願輸入免費的帳號資訊生成音樂。 每個帳戶每天可以免費生成五首歌曲，我們不會將它們用於其他目的。請放心使用！如果有10000名用戶，那麼系統每天可以免費生成50000首歌曲。請儘量節省使用量，因為每個帳戶每天只能免費生成五首歌曲。如果每個人每天創作五首以上的歌曲，這仍然不够。 最終目標是讓在需要的時候能隨時免費生成。


### Buy me a Coffee

<a href="https://www.buymeacoffee.com/SunoApi" target="_blank"><img src="https://sunoapi.net/images/donate.jpg" alt="Buy me a Coffee" style="max-width: 100%;"></a>


##### 此項目開源於GitHub，基於MIT協定且免費，沒有任何形式的付費行為！如果你覺得此項目對你有幫助，請幫我點個Star並轉發擴散，在此感謝你！