# from pathlib import Path

import pandas as pd
# import streamlit as st
import requests



# path = Path(__file__).parent / "dummy_data.csv"
# df_dummy = pd.read_csv(path.as_uri(), dtype=str)

# url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=100"
# # payload = {'key1': 10, 'key2': 'string'}
# res = requests.get(url)
# print(res.text)

# st.dataframe(df_dummy)

import folium
import streamlit as st
from streamlit_folium import st_folium
import json

from pathlib import Path
import folium
# import streamlit as st
import geopandas as gpd
# from streamlit_folium import st_folium


# タイトル
# st.title("サンプルアプリ")

st.set_page_config(
    page_title="名刺交換者ヒートマップ",
    page_icon="🗾",
    layout="wide"
)

name = st.text_input('名前', placeholder='名前', max_chars=10, help='英字で始めること')
# passwd = st.text_input('パスワード', type='password', max_chars=20)
# st.write(f'ユーザIDは {userid} です。パスワードは、もちろん秘密です。')

if st.button('押してみる'):
    # # payload = {'key1': 10, 'key2': 'string'}
    # res = requests.get(url)
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/count"
    # payload = {'key1': 10, 'key2': 'string'}
    res = requests.get(url)
    print(res.text)

    card_num = res.text

    # url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=" + card_num
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=2000" 
    # url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/count"
    # payload = {'key1': 10, 'key2': 'string'}
    res = requests.get(url)
    print(res.text)

    card_data = res.text
    # JSONデータをパース
    data = json.loads(card_data)
    # for i in range(data):
        

    # パースしたデータをpandasのデータフレームに変換
    df = pd.DataFrame(data)

    # データフレームを表示
    print(df)
    # 検索したい名前を定義
    search_name = "後藤 裕太"

    # full_nameカラムで検索
    result = df[df['full_name'] == search_name]

    # user_id.reset_index(drop=True)
    # user_id = result["user_id"].to_list()
    user_id = result["user_id"].iloc[0]
    company_id = result["company_id"].iloc[0]

    print(user_id)
    print(company_id)
    # st.write(f'user_id:{user_id}' )
    # st.write(f'company_id:{company_id}')
    
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/" + user_id + "?offset=0&limit=100"
    print(url)

    res = requests.get(url)
    print(res.text)

    # prefecture_count

    new_data = json.loads(res.text)
    # new_data = json.loads(maishi_data)

    # データフレームに変換
    # df = pd.DataFrame(new_data)
    new_df = pd.DataFrame(new_data)
    new_df['user_id'] = new_df['user_id'].astype(str)

    # user_idで住所を参照
    address_map = df.set_index('user_id')['address'].to_dict()
    print(1)
    print(address_map)
    new_df['address'] = new_df['user_id'].map(address_map)



    # 都道府県ごとに計測
    # new_df['prefecture'] = new_df['address'].str.extract(r'^(.*?県)')
    new_df['prefecture'] = new_df['address'].str.extract(r'(.*?[都道府県])')
    print(new_df)
    prefecture_count = new_df['prefecture'].value_counts()

    # 結果を表示
    print(prefecture_count)


    COLUMNS = ["Prefecture_name", "Prefecture_code", "Infections"]
    PREFECTURES_CODE = {
        1: '北海道', 2: '青森県', 3: '岩手県', 4: '宮城県', 5: '秋田県',
        6: '山形県', 7: '福島県', 8: '茨城県', 9: '栃木県', 10: '群馬県',
        11: '埼玉県', 12: '千葉県', 13: '東京都', 14: '神奈川県', 15: '新潟県',
        16: '富山県', 17: '石川県', 18: '福井県', 19: '山梨県', 20: '長野県',
        21: '岐阜県', 22: '静岡県', 23: '愛知県', 24: '三重県', 25: '滋賀県',
        26: '京都府', 27: '大阪府', 28: '兵庫県', 29: '奈良県', 30: '和歌山県',
        31: '鳥取県', 32: '島根県', 33: '岡山県', 34: '広島県', 35: '山口県',
        36: '徳島県', 37: '香川県', 38: '愛媛県', 39: '高知県', 40: '福岡県',
        41: '佐賀県', 42: '長崎県', 43: '熊本県', 44: '大分県', 45: '宮崎県',
        46: '鹿児島県', 47: '沖縄県'
    }

    # datasets = df

    prefecture_data = [] 
    for code, prefecture in PREFECTURES_CODE.items():
        # print(code)
        # print(prefecture)
        if prefecture in prefecture_count:
            counts = prefecture_count[prefecture]
        else:
            counts = 0
        prefecture_data.append([prefecture, code, counts])
        # print([prefecture, code, counts])


    print(prefecture_data)
    df2 = pd.DataFrame(prefecture_data, columns=COLUMNS)
    print(df2)


    # print(result)
    GEOJSON_PATH = "app/japan.geojson"

    map = folium.Map(
        location=(36.56583, 139.88361),
        tiles="cartodbpositron",
        zoom_start=5
    )

    geojson = gpd.read_file(GEOJSON_PATH)
    # folium.GeoJson(geojson).add_to(map)


    choropleth = folium.Choropleth(
        geo_data=geojson,
        data=df2,
        columns=["Prefecture_code", "Infections"],
        key_on="feature.properties.id",
        fill_color='YlOrRd',
        nan_fill_color='darkgray',
        fill_opacity=0.8,
        nan_fill_opacity=0.8,
        line_opacity=0.2,
    ).add_to(map)

    choropleth.add_to(map)

    # カスタムCSSを追加しないように修正
    for key in choropleth._children:
        if key.startswith('color_map'):
            del choropleth._children[key]

    # st_folium(map, use_container_width=True, height=720)
    # st_folium(map, use_container_width=True, height=720)
    st_folium(map, use_container_width=True, height=720, returned_objects=[])

# else:
    # st.write('むむむ')

