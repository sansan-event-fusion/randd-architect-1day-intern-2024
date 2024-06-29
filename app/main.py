import json

import folium
import geopandas as gpd
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="名刺交換者ヒートマップ", page_icon="🗾", layout="wide")

name = st.text_input("名前", placeholder="名前", max_chars=10, help="名前と名字の間は半角空白を入れてください")

if st.button("自分の名刺交換者"):
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/count"
    res = requests.get(url)  # noqa: S113
    card_num = res.text

    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=" + card_num
    res = requests.get(url)  # noqa: S113

    card_data = res.text
    # JSONデータをパース
    card_data = json.loads(card_data)

    # パースしたデータをpandasのデータフレームに変換
    card_data_df = pd.DataFrame(card_data)
    # 検索したい名前を定義
    search_name = name

    # full_nameカラムで検索
    result = card_data_df[card_data_df["full_name"] == search_name]
    user_id = result["user_id"].iloc[0]
    company_id = result["company_id"].iloc[0]

    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/" + user_id + "?offset=0&limit=100"

    res = requests.get(url)  # noqa: S113

    I_have_maishi_df = json.loads(res.text)
    I_have_maishi_df = pd.DataFrame(I_have_maishi_df)
    I_have_maishi_df["user_id"] = I_have_maishi_df["user_id"].astype(str)

    # user_idで住所を参照
    I_address_map = card_data_df.set_index("user_id")["address"].to_dict()
    I_have_maishi_df["address"] = I_have_maishi_df["user_id"].map(I_address_map)

    # 都道府県ごとに計測
    I_have_maishi_df["prefecture"] = I_have_maishi_df["address"].str.extract(r"(.*?[都道府県])")
    I_prefecture_count = I_have_maishi_df["prefecture"].value_counts()

    COLUMNS = ["Prefecture_name", "Prefecture_code", "Infections"]
    PREFECTURES_CODE = {
        1: "北海道",
        2: "青森県",
        3: "岩手県",
        4: "宮城県",
        5: "秋田県",
        6: "山形県",
        7: "福島県",
        8: "茨城県",
        9: "栃木県",
        10: "群馬県",
        11: "埼玉県",
        12: "千葉県",
        13: "東京都",
        14: "神奈川県",
        15: "新潟県",
        16: "富山県",
        17: "石川県",
        18: "福井県",
        19: "山梨県",
        20: "長野県",
        21: "岐阜県",
        22: "静岡県",
        23: "愛知県",
        24: "三重県",
        25: "滋賀県",
        26: "京都府",
        27: "大阪府",
        28: "兵庫県",
        29: "奈良県",
        30: "和歌山県",
        31: "鳥取県",
        32: "島根県",
        33: "岡山県",
        34: "広島県",
        35: "山口県",
        36: "徳島県",
        37: "香川県",
        38: "愛媛県",
        39: "高知県",
        40: "福岡県",
        41: "佐賀県",
        42: "長崎県",
        43: "熊本県",
        44: "大分県",
        45: "宮崎県",
        46: "鹿児島県",
        47: "沖縄県",
    }

    I_prefecture_data = []
    for code, prefecture in PREFECTURES_CODE.items():
        counts = I_prefecture_count.get(prefecture, 0)
        I_prefecture_data.append([prefecture, code, counts])

    my_count_df = pd.DataFrame(I_prefecture_data, columns=COLUMNS)

    GEOJSON_PATH = "app/japan.geojson"

    map = folium.Map(  # noqa: A001
        location=(36.56583, 139.88361), tiles="cartodbpositron", zoom_start=5
    )

    geojson = gpd.read_file(GEOJSON_PATH)

    My_choropleth = folium.Choropleth(
        geo_data=geojson,
        data=my_count_df,
        columns=["Prefecture_code", "Infections"],
        key_on="feature.properties.id",
        fill_color="YlOrRd",
        nan_fill_color="darkgray",
        fill_opacity=0.8,
        nan_fill_opacity=0.8,
        line_opacity=0.2,
    ).add_to(map)

    My_choropleth.add_to(map)
    # カスタムCSSを追加しないように修正
    for key in My_choropleth._children:  # noqa: SLF001
        if key.startswith("color_map"):
            del My_choropleth._children[key]  # noqa: SLF001

    st_folium(map, use_container_width=True, height=720, returned_objects=[])

elif st.button("自社の名刺交換者"):
    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/count"
    res = requests.get(url)  # noqa: S113
    card_num = res.text

    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=" + card_num
    res = requests.get(url)  # noqa: S113

    card_data = res.text
    # JSONデータをパース
    card_data = json.loads(card_data)

    # パースしたデータをpandasのデータフレームに変換
    card_data_df = pd.DataFrame(card_data)
    # 検索したい名前を定義
    search_name = name

    # full_nameカラムで検索
    result = card_data_df[card_data_df["full_name"] == search_name]
    user_id = result["user_id"].iloc[0]
    company_id = result["company_id"].iloc[0]

    url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_companies/" + company_id + "?offset=0&limit=100"
    res = requests.get(url)  # noqa: S113

    Com_have_maishi_df = json.loads(res.text)
    Com_have_maishi_df = pd.DataFrame(Com_have_maishi_df)
    Com_have_maishi_df["company_id"] = Com_have_maishi_df["company_id"].astype(str)

    # user_idで住所を参照
    Com_address_map = card_data_df.set_index("company_id")["address"].to_dict()
    Com_have_maishi_df["address"] = Com_have_maishi_df["company_id"].map(Com_address_map)

    # 都道府県ごとに計測
    Com_have_maishi_df["prefecture"] = Com_have_maishi_df["address"].str.extract(r"(.*?[都道府県])")
    Com_prefecture_count = Com_have_maishi_df["prefecture"].value_counts()

    COLUMNS = ["Prefecture_name", "Prefecture_code", "Infections"]
    PREFECTURES_CODE = {
        1: "北海道",
        2: "青森県",
        3: "岩手県",
        4: "宮城県",
        5: "秋田県",
        6: "山形県",
        7: "福島県",
        8: "茨城県",
        9: "栃木県",
        10: "群馬県",
        11: "埼玉県",
        12: "千葉県",
        13: "東京都",
        14: "神奈川県",
        15: "新潟県",
        16: "富山県",
        17: "石川県",
        18: "福井県",
        19: "山梨県",
        20: "長野県",
        21: "岐阜県",
        22: "静岡県",
        23: "愛知県",
        24: "三重県",
        25: "滋賀県",
        26: "京都府",
        27: "大阪府",
        28: "兵庫県",
        29: "奈良県",
        30: "和歌山県",
        31: "鳥取県",
        32: "島根県",
        33: "岡山県",
        34: "広島県",
        35: "山口県",
        36: "徳島県",
        37: "香川県",
        38: "愛媛県",
        39: "高知県",
        40: "福岡県",
        41: "佐賀県",
        42: "長崎県",
        43: "熊本県",
        44: "大分県",
        45: "宮崎県",
        46: "鹿児島県",
        47: "沖縄県",
    }

    Com_prefecture_data = []
    for code, prefecture in PREFECTURES_CODE.items():
        counts = Com_prefecture_count.get(prefecture, 0)
        Com_prefecture_data.append([prefecture, code, counts])

    Com_count_df = pd.DataFrame(Com_prefecture_data, columns=COLUMNS)

    GEOJSON_PATH = "app/japan.geojson"

    map = folium.Map(  # noqa: A001
        location=(36.56583, 139.88361), tiles="cartodbpositron", zoom_start=5
    )

    geojson = gpd.read_file(GEOJSON_PATH)

    Com_choropleth = folium.Choropleth(
        geo_data=geojson,
        data=Com_count_df,
            columns=["Prefecture_code", "Infections"],
        key_on="feature.properties.id",
        fill_color="YlOrRd",
        nan_fill_color="darkgray",
        fill_opacity=0.8,
        nan_fill_opacity=0.8,
        line_opacity=0.2,
    ).add_to(map)

    Com_choropleth.add_to(map)

    for key in Com_choropleth._children:  # noqa: SLF001
        if key.startswith("color_map"):
            del Com_choropleth._children[key]  # noqa: SLF001

    st_folium(map, use_container_width=True, height=720, returned_objects=[])
