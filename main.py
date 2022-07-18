#!/usr/bin/env python3

"""
Twitter APIから地域ごとのトレンドワードのトップ50ランキングを取得します。
ランキング上位のキーワードの文字が大きくなる簡易的なワードクラウドを作成します。
キーワードの記事検索を行い、キーワードの関連情報を取得します。
"""

#必要なモジュールのインポート
from datetime import datetime, timedelta
import requests
import pandas as pd
import tweepy
from wordcloud import WordCloud
import folium
import streamlit as st
from streamlit_folium import folium_static
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
         "さいたま": 1116753,
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
         "沖縄": 2345896}

# 地図用データ
city_data = pd.DataFrame(
    data =[[35.685454, 139.752821, 126146099], [43.062083, 141.354389, 1962115],
           [38.268222, 140.869417, 1098309], [35.861389, 139.645556, 1338762],
           [35.689556, 139.691722, 14029726], [35.607278, 140.106361, 978461],
           [35.450333, 139.634222, 3774369], [35.530889, 139.703, 1542257],
           [35.571417, 139.373139, 726485], [37.916194, 139.036389, 779907],
           [34.710833, 137.7275, 783856], [35.181389, 136.906389, 2326239],
           [35.011611, 135.768111, 1449381], [34.69375, 135.502111, 2753149],
           [34.690167, 135.195444, 1512287], [34.655111, 133.919583, 719968],
           [34.38525, 132.455306, 1192547], [34.342806, 134.046611,	414519],
           [33.883417, 130.875194, 926179], [33.590139, 130.401722, 1627244],
           [32.803, 130.707861,	737423], [26.212444, 127.680917, 1467800]],

    index=["日本", "札幌", "仙台", "さいたま", "東京", "千葉",
           "横浜", "川崎", "相模原", "新潟", "浜松", "名古屋",
           "京都", "大阪", "神戸", "岡山", "広島", "高松",
           "北九州", "福岡", "熊本", "沖縄"],
    columns=["x","y", "population"])

api = authTwitter()
trend_data = []
word_cloud_data = []
japan_time = datetime.now() + timedelta(hours=9)

# 都市名を指定してトレンドランキングを取得
def trend(city):
    wid = woeid[city]    
    trends = api.get_place_trends(wid)[0]
    df = pd.DataFrame(columns = ["順位" , "ワード"])
    for i, content in enumerate(trends["trends"]):
        [a, b] = [i+1, content["name"]]
        df.loc[i+1] = [a, b]        
        trend_data.append(b)
        word_cloud_data.append((b + " ") * (51 - i)) # ランキング上位の要素数を増やす
    return df
    
# キーワードを指定して記事検索
def news_search(query):
    if query[0] == "#":
        query = query[1:]    
    params = {
    'q': query,
    'sortBy': 'publishedAt',
    'pageSize': 30}
    response = requests.get(URL, headers=HEADERS, params=params)
    data = response.json()             
    return data        

# データクラウドの画像表示
def word_cloud():
    text = " ".join(word_cloud_data)
    wc = WordCloud(background_color="white",
                   font_path = FONT_PATH,
                   collocations = False,            
                   max_font_size=100).generate(text)
    wc.to_file("trend_data.png")

# 地図を表示
def AreaMarker(df, m):
    for index, r in df.iterrows():
        if index == genre:
            folium.Marker(location=[r.x, r.y], popup=index).add_to(m)
            folium.Circle(
                radius= 10000,
                location=[r.x, r.y],
                popup=index,
                color="yellow",
                fill=True,
                fill_opacity=0.07).add_to(m)

# サイドバーにラジオボタンを作成
genre = st.sidebar.radio(
     "都市名・地域名を選択してください",
     ("日本", "札幌", "仙台", "さいたま", "東京", "千葉",
      "横浜", "川崎", "相模原", "新潟", "浜松", "名古屋",     
      "京都", "大阪", "神戸", "岡山", "広島", "高松",
      "北九州", "福岡", "熊本", "沖縄"))

st.title('Twitter トレンドランキング')
st.write(japan_time.strftime("%Y/%m/%d %H:%M:%S"))

population = city_data.at[genre,"population"]
st.subheader(f"{genre}: 人口{population:,}人")
m = folium.Map(location=[city_data.at[genre,"x"], 
               city_data.at[genre,"y"]], zoom_start=7)
AreaMarker(city_data, m) # データを地図に渡す
folium_static(m) # 地図情報を表示

# トレンドワードランキングを表示
st.subheader(f"{genre}: トレンドワード Top50")
df1 = trend(genre)
st.table(df1)

# ワードクラウドを表示
st.subheader(f"{genre}: ワードクラウドでトレンド表示")
st.write("※ランキングを文字サイズに反映しています")
word_cloud()
image = Image.open("trend_data.png")
st.image(image, caption="Twitterトレンドワード",use_column_width=True)

# 記事検索結果を表示
st.subheader("トレンドワード（Top5)の関連記事を検索")
for word in trend_data[:5]:
    data = news_search(word)
    st.write("トレンドワード", word)
    st.write("記事検索結果：", data["totalResults"])
    if data["totalResults"] > 0:
        df2 = pd.DataFrame(data["articles"])
        st.dataframe(df2[["publishedAt", "title", "url"]])
