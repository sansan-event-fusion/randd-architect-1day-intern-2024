import json
import time

import requests
import streamlit as st

# タイトル
st.title("サンプルアプリ")


def get_coordinates(data):  # noqa: C901
    address = data["address"]

    prefectures = [
        "北海道",
        "青森県",
        "岩手県",
        "宮城県",
        "秋田県",
        "山形県",
        "福島県",
        "茨城県",
        "栃木県",
        "群馬県",
        "埼玉県",
        "千葉県",
        "東京都",
        "神奈川県",
        "新潟県",
        "富山県",
        "石川県",
        "福井県",
        "山梨県",
        "長野県",
        "岐阜県",
        "静岡県",
        "愛知県",
        "三重県",
        "滋賀県",
        "京都府",
        "大阪府",
        "兵庫県",
        "奈良県",
        "和歌山県",
        "鳥取県",
        "島根県",
        "岡山県",
        "広島県",
        "山口県",
        "徳島県",
        "香川県",
        "愛媛県",
        "高知県",
        "福岡県",
        "佐賀県",
        "長崎県",
        "熊本県",
        "大分県",
        "宮崎県",
        "鹿児島県",
        "沖縄県",
    ]

    for prefecture in prefectures:
        if prefecture in address:
            # Split the address to extract the city or town
            remaining_address = address.split(prefecture)[1]
            # Extract city or town name
            if "市" in remaining_address:
                city_name = remaining_address.split("市")[0] + "市"
            elif "町" in remaining_address:
                city_name = remaining_address.split("町")[0] + "町"
            elif "村" in remaining_address:
                city_name = remaining_address.split("村")[0] + "村"
            elif "区" in remaining_address:
                city_name = remaining_address.split("区")[0] + "区"

    city_hall = city_name + "役所"
    get_adress_url = "https://msearch.gsi.go.jp/address-search/AddressSearch?q=" + city_hall
    coordinates_response = requests.get(get_adress_url, timeout=10)
    coordinates = coordinates_response.json()[0]["geometry"]["coordinates"]
    return coordinates[0], coordinates[1]


def find_user_id(full_name, company_name, users):
    for user in users:
        if user["full_name"] == full_name and user["company_name"] == company_name:
            return user["user_id"]
    return None


with st.form("my_form", clear_on_submit=False):
    name = st.text_input("名前を入力してください")
    company = st.text_input("企業名を入力してください")
    submitted = st.form_submit_button("検索")

# カードのデータを全件取得する
user_id_search_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=1&limit=10000"
users = requests.get(url=user_id_search_url, timeout=10).json()

if submitted:
    with st.spinner("検索中です..."):
        time.sleep(3)
        user_id = find_user_id(full_name=name, company_name=company, users=users)
        top_10_search_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/" + user_id + "/similar_top10_users"
        r = requests.get(url=top_10_search_url, timeout=10)

        response_body = r.text
        response_body = json.loads(response_body)
        pref_list = []
        for data in response_body:
            longtitude, latitude = get_coordinates(data=data)
            pref_list.append({"longitude":longtitude, "latitude":latitude})
        st.map(pref_list)
else:
    st.write("名前と企業名を入力してください。")
