import pandas as pd
import requests
import streamlit as st

# title
st.title("Sansan")

contact_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/?offset=0&limit=100"

response = requests.get(contact_url, timeout=10)
contact_data = response.json()

# n番目のインデックスを指定
n = 0  # 例として0番目を指定

# n番目のインデックスにあるowner_user_idを取得
if isinstance(contact_data, list) and n < len(contact_data) and "owner_user_id" in contact_data[n]:
    owner_user_id = contact_data[n]["owner_user_id"]

st.write(f"オーナーユーザーID: {owner_user_id}")

# オーナーユーザーIDに紐づいているユーザー情報を取得
owner_user_url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{owner_user_id}?offset=0&limit=100"

response = requests.get(owner_user_url, timeout=10)
owner_user_data = response.json()

# owner_user_dataに紐づいているユーザー情報(user_idから情報)を取得し、それだけをまとめる
user_ids = []  # 空のリストを作成
for n in range(len(owner_user_data)):
    get_user_id = owner_user_data[n]["user_id"]
    get_create_at = owner_user_data[n]["created_at"]
    user_ids.append((get_user_id,get_create_at)) # get_user_idをリストに格納

# ここで時系列順にsortを行う
user_ids.sort(key=lambda x: x[1])

# user_idsに紐づいているユーザー情報を取得
user_data = []  # 空のリストを作成
for index in user_ids:
    user_id = index[0]
    user_url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}"
    response = requests.get(user_url, timeout=10)
    user_info = (response.json())

    # フラットなリストに変換
    if isinstance(user_info, list):
        user_data.extend(user_info)
    else:
        user_data.append(user_info)

st.write(
    pd.DataFrame(user_data)[["full_name", "position", "company_name", "address", "phone_number"]]
)

