import folium
from streamlit_folium import folium_static
import streamlit as st
import requests
import re
from collections import defaultdict
import pandas as pd

def get_cards():
    url = 'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=1000'
    response = requests.get(url)
    return response.json()

def count_companies_by_prefecture(data):
    prefecture_pattern = re.compile(r'^(北海道|青森県|岩手県|宮城県|秋田県|山形県|福島県|茨城県|栃木県|群馬県|埼玉県|千葉県|東京都|神奈川県|新潟県|富山県|石川県|福井県|山梨県|長野県|岐阜県|静岡県|愛知県|三重県|滋賀県|京都府|大阪府|兵庫県|奈良県|和歌山県|鳥取県|島根県|岡山県|広島県|山口県|徳島県|香川県|愛媛県|高知県|福岡県|佐賀県|長崎県|熊本県|大分県|宮崎県|鹿児島県|沖縄県)')
    company_count_by_prefecture = defaultdict(int)
    
    for item in data:
        address = item['address']
        match = prefecture_pattern.match(address)
        if match:
            prefecture = match.group(1)
            company_count_by_prefecture[prefecture] += 1
    
    result_dict = dict(company_count_by_prefecture)
    print(result_dict)
    return result_dict

def organize_data_by_prefecture():
    data = get_cards()
    prefecture_pattern = re.compile(r'^(北海道|青森県|岩手県|宮城県|秋田県|山形県|福島県|茨城県|栃木県|群馬県|埼玉県|千葉県|東京都|神奈川県|新潟県|富山県|石川県|福井県|山梨県|長野県|岐阜県|静岡県|愛知県|三重県|滋賀県|京都府|大阪府|兵庫県|奈良県|和歌山県|鳥取県|島根県|岡山県|広島県|山口県|徳島県|香川県|愛媛県|高知県|福岡県|佐賀県|長崎県|熊本県|大分県|宮崎県|鹿児島県|沖縄県)')
    data_by_prefecture = defaultdict(list)

    for item in data:
        address = item['address']
        match = prefecture_pattern.match(address)
        if match:
            prefecture = match.group(1)
            company_info = {
                '氏名': item['full_name'],
                '役職': item['position'],
                '会社名': item['company_name'],
                '住所': item['address'],
                '電話番号': item['phone_number']
            }
            data_by_prefecture[prefecture].append(company_info)
    return dict(data_by_prefecture)

company_count_by_prefecture = {'千葉県': 78, '三重県': 10, '広島県': 55, '東京都': 171, '京都府': 13, '佐賀県': 10, '埼玉県': 61, '大分県': 13, '宮崎県': 24, '富山県': 22, '山口県': 6, '山形県': 10, '山梨県': 18, '岩手県': 22, '島根県': 24, '徳島県': 12, '愛媛県': 20, '滋賀県': 11, '熊本県': 9, '石川県': 8, '福井県': 26, '福島県': 8, '秋田県': 17, '長崎県': 9, '長野県': 9, '青森県': 7, '香川県': 25, '鳥取県': 16, '神奈川県': 43, '兵庫県': 37, '北海道': 38, '奈良県': 13, '岐阜県': 16, '栃木県': 16, '沖縄県': 9, '福岡県': 34, '群馬県': 8, '茨城県': 5, '高知県': 9, '鹿児島県': 9, '和歌山県': 9, '大阪府': 11, '岡山県': 18, '愛知県': 11}

# 都道府県の中心の緯度経度を設定
prefecture_coords = {
    '北海道': [43.06417, 141.34694], '青森県': [40.82444, 140.74], '岩手県': [39.70361, 141.1525],
    '宮城県': [38.26889, 140.87194], '秋田県': [39.71861, 140.1025], '山形県': [38.24056, 140.36333],
    '福島県': [37.75, 140.46778], '茨城県': [36.34139, 140.44667], '栃木県': [36.56583, 139.88361],
    '群馬県': [36.39111, 139.06083], '埼玉県': [35.85694, 139.64889], '千葉県': [35.60472, 140.12333],
    '東京都': [35.68944, 139.69167], '神奈川県': [35.44778, 139.6425], '新潟県': [37.90222, 139.02361],
    '富山県': [36.69528, 137.21139], '石川県': [36.59444, 136.62556], '福井県': [36.06528, 136.22194],
    '山梨県': [35.66389, 138.56833], '長野県': [36.65139, 138.18111], '岐阜県': [35.39111, 136.72222],
    '静岡県': [34.97694, 138.38306], '愛知県': [35.18028, 136.90667], '三重県': [34.73028, 136.50861],
    '滋賀県': [35.00444, 135.86833], '京都府': [35.02139, 135.75556], '大阪府': [34.68639, 135.52],
    '兵庫県': [34.69139, 135.18306], '奈良県': [34.68528, 135.83278], '和歌山県': [34.22611, 135.1675],
    '鳥取県': [35.50361, 134.23833], '島根県': [35.47222, 133.05056], '岡山県': [34.66167, 133.935],
    '広島県': [34.39639, 132.45944], '山口県': [34.18583, 131.47139], '徳島県': [34.06583, 134.55944],
    '香川県': [34.34028, 134.04333], '愛媛県': [33.84167, 132.76611], '高知県': [33.55972, 133.53111],
    '福岡県': [33.60639, 130.41806], '佐賀県': [33.24944, 130.29889], '長崎県': [32.74472, 129.87361],
    '熊本県': [32.78972, 130.74167], '大分県': [33.23806, 131.6125], '宮崎県': [31.91111, 131.42389],
    '鹿児島県': [31.56028, 130.55806], '沖縄県': [26.2125, 127.68111]
}

# 各都道府県の会社数に比例した円を作成する関数
def add_prefecture_circles(m, data, coords):
    for prefecture, count in data.items():
        if prefecture in coords:
            folium.CircleMarker(
                location=coords[prefecture],
                radius=count / 3,  # 会社数に比例して円のサイズを調整
                tooltip=f'{prefecture}: {count}社',
                color='red',
                fill=True,
                fill_color='red',
                fill_opacity=0.6
            ).add_to(m)

def display_data_by_prefecture(prefecture, data):
    if prefecture in data:
        df = pd.DataFrame(data[prefecture])
        st.write(f"### {prefecture}: {len(data[prefecture])}社")
        st.dataframe(df)
    else:
        st.write(f"### {prefecture}: 0社")


# ------------------------画面作成------------------------

st.title("会社数分布地図") # タイトル
m = folium.Map(location=[35.68944, 139.69167], zoom_start=6) # 地図の初期設定
add_prefecture_circles(m, company_count_by_prefecture, prefecture_coords)  # 都道府県ごとの会社数に基づく円を追加
folium_static(m) # 地図情報を表示

organized_data = organize_data_by_prefecture()

# 都道府県選択のためのセレクトボックス
selected_prefecture = st.selectbox("都道府県を選択してください", list(organized_data.keys()))
# 選択された都道府県のデータを表示
display_data_by_prefecture(selected_prefecture, organized_data)
