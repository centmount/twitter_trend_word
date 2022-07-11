#!/usr/bin/env python3

"""
Twitter APIからトップ50のランキングのデータを取得します。

"""

#必要なモジュールのインポート
from datetime import datetime
import requests
import pandas as pd
import tweepy
from wordcloud import WordCloud
import streamlit as st
from PIL import Image

st.set_page_config(layout="wide")

# パスワードはstreamlitのシークレットに保存
# パスワード入力
def login():
    value = st.sidebar.text_input('パスワードを入力してください:', type='password')
    if value == st.secrets['PASSWORD']:
        st.sidebar.write('パスワードを確認しました！')
    else:
        st.stop()

login()



# Twitter API認証キーの設定
CONSUMER_KEY = st.secrets['CONSUMER_KEY']
CONSUMER_SECRET = st.secrets['CONSUMER_SECRET']
ACCESS_KEY = st.secrets['ACCESS_KEY']
ACCESS_SECRET = st.secrets['ACCESS_SECRET']

# News APIの設定
HEADERS = {"X-Api-Key": st.secrets['NEWS_API_KEY']}
URL = "https://newsapi.org/v2/everything"

# FONTファイルの設定
FONT_PATH = "./Noto_Sans_JP/NotoSansJP-Regular.otf"

# OAuth認証
def authTwitter():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

    #APIインスタンスを作成、レート制限が補充されるまで待機
    api = tweepy.API(auth, wait_on_rate_limit = True)
    return(api)

#トレンドランキングを取得できる日本の都市
woeid = {"日本": 23424856,
         "札幌": 1118108,
         "仙台": 1118129,                           
         "埼玉": 1116753,
         "東京": 1118370,
         "千葉": 1117034,
         "横浜": 1118550,
         "川崎": 1117502, 
         "相模原": 1118072,
         "新潟": 1117881,
         "浜松": 1117155,        
         "名古屋": 1117817,        
         "京都": 15015372,
         "大阪": 15015370,
         "神戸": 1117545,         
         "岡山": 90036018,
         "広島": 1117227,
         "高松": 1118285,
         "北九州": 1110809,
         "福岡": 1117099,         
         "熊本": 1117605,
         "沖縄": 2345896
         }

api = authTwitter()
trend_data = []
word_cloud_data = []
now = datetime.now()
df1 = pd.DataFrame(columns = ["順位", "ワード"])
df2 = pd.DataFrame()

# 都市名を指定してトレンドランキングを取得
def trend(city):
    wid = woeid[city]    
    trends = api.get_place_trends(wid)[0]
    for i, content in enumerate(trends["trends"]):
        [a, b] = [i+1, content["name"]]
        df1 = df1.append([a, b])
        trend_data.append(b)
        word_cloud_data.append((b + " ") * (51 - i))
        return df1
    
# キーワードを指定して記事検索
def news_search(query):
    if query[0] == "#":
        query = query[1:]    
    params = {
    'q': query,
    'sortBy': 'publishedAt',
    'pageSize': 100}
    response = requests.get(URL, headers=HEADERS, params=params)
    pd.options.display.max_colwidth = 25

    if response.ok:
        data = response.json()
        df2 = df2.append(data['articles'])
        st.write('trend_word: ', query, 'totalResults:', data['totalResults'])
        if data['totalResults'] > 0:
            st.dataframe(df2[[ 'publishedAt', 'title', 'url']])
        

# データクラウドの画像表示
def word_cloud():
    text = " ".join(word_cloud_data)
    wc = WordCloud(background_color="white",
                   font_path = FONT_PATH,
                   collocations = False,            
                   max_font_size=100).generate(text)
    wc.to_file("trend_data.png")

st.title('Twitter トレンドランキング')

# サイドバーにラジオボタンを作成
genre = st.sidebar.radio(
     "都市名を選択してください",
     ("日本", "札幌", "仙台", "埼玉", "東京", "千葉",
      "横浜", "川崎", "相模原", "新潟", "浜松", "名古屋",     
      "京都", "大阪", "神戸", "岡山", "広島", "高松",
      "北九州", "福岡", "熊本", "沖縄"))

st.write(genre)
st.write(now.strftime("%Y/%m/%d %H:%M:%S"))

trend(genre)

st.dataframe(df1)

for word in trend_data:
    news_search(word)

word_cloud()
image = Image.open('trend_data.png')
st.image(image, caption='Twitterトレンドワード',use_column_width=True)







