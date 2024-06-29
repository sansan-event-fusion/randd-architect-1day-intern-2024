from pathlib import Path

import pandas as pd
import streamlit as st
import requests


#cardsの数を取得
url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/count"

count_cards = requests.get(url)

#cardsを全て取得
url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=" + count_cards.text

# GETリクエストを送信してデータを取得
response = requests.get(url)

data = response.json()  # JSONデータを取得

# データをDataFrameに変換
df_cards = pd.DataFrame(data)

# st.subheader("df_cards")
# st.dataframe(df_cards)


#contactsの数を取得
url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/count"

count_contacts = requests.get(url)

#contactsを全て取得
url = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/?offset=0&limit=" + count_cards.text

# GETリクエストを送信してデータを取得
response = requests.get(url)

data = response.json()  # JSONデータを取得

# データをDataFrameに変換
df_contacts = pd.DataFrame(data)

# st.subheader("df_contacts")
# st.dataframe(df_contacts)





#user結合
merged_df = pd.merge(df_contacts, df_cards.loc[:, ['user_id', 'position', 'company_name']], on='user_id', how='left')
merged_df = merged_df.rename(columns={'company_name': 'user_company_name', 'position': 'user_position'})


#owner結合
merged_df = pd.merge(merged_df, df_cards.loc[:, ['user_id', 'position', 'company_name']], left_on='owner_user_id', right_on='user_id', how='left')
merged_df = merged_df.rename(columns={'company_name': 'owner_company_name',
                               'position': 'owner_position'})

# # # APIデータをテーブル形式で表示
# st.subheader("merged_df")
# st.dataframe(merged_df)

df_position_user = merged_df.pivot_table(index='owner_company_id', columns='user_position', aggfunc='size', fill_value=0)

# st.subheader("APIから取得したデータ")
# st.subheader(df_position_user.shape)
# st.dataframe(df_position_user)




# テストケース
unique_company_names = df_cards['company_name'].unique()

# ユニークなcompany_nameを表示
st.subheader('社名一覧')
st.dataframe(unique_company_names)


import networkx as nx

# グラフの作成
G = nx.Graph()

# ノードとエッジの追加
for index, row in merged_df.iterrows():
    G.add_edge(row['owner_user_id'], row['user_id_x'], company=row['owner_company_name'])

def find_routes(df, owner_company_name, user_company_name):
    routes = []
    for index, row in df.iterrows():
        if row['owner_company_name'] == owner_company_name and row['user_company_name'] == user_company_name:
            try:
                path = nx.shortest_path(G, source=row['owner_user_id'], target=row['user_id_x'])
                routes.append((path, len(path)))
            except nx.NetworkXNoPath:
                continue
    # ホップ数でソート
    routes = sorted(routes, key=lambda x: x[1])
    # 上位5つを返す
    return routes[:5]







owner_company_name = '松本農林株式会社'
user_company_name = '株式会社中島情報'

with st.form(key='input_form'):
    owner_company_name = st.text_input('オーナー会社名')
    user_company_name = st.text_input('ユーザー会社名')
    submit_button = st.form_submit_button(label='送信')




if submit_button:
    if owner_company_name and user_company_name:
        routes = find_routes(merged_df, owner_company_name, user_company_name)
        st.subheader(owner_company_name + ' -> ' + user_company_name + ': ')
        for route in routes:
            st.subheader(route[0])
            for id in route[0]:
                st.dataframe(df_cards[df_cards['user_id'] == id])


