import streamlit as st
import requests
import pandas as pd
import openai
from dotenv import load_dotenv
import os
import re

# 環境変数をロード
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv('OPENAI_API_KEY')

# タイトル
st.title("営業先推薦アプリ")

# user_idの入力を受け取る部分
user_id = st.text_input("あなたのユーザーIDを入力してください:")


def get_all_user():
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=100'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        return None


# APIからユーザーのデータを取得する関数
def get_user_data(user_id):
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        return None
    
# APIからユーザーの名刺をもつ人を取得
def get_user_contacts(user_id):
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        return None

# APIから名刺を所持している人のデータを取得する関数
def get_owner_users(user_id):
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{user_id}?offset=0&limit=100'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        return None

# APIから推薦データを取得する関数
def get_similar_users(text):
    # 正規表現を使って数字だけを抜き出す
    numbers = re.findall(r'\d+', text)

    # 数字のリストを結合して1つの文字列にする
    user_id = ''.join(numbers)

    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}/similar_top10_users'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        return None

# OpenAI APIを利用してさらなる推薦を取得する関数
def get_additional_recommendations(user_data, similar_users_data, criteria):
    # プロンプトを生成する
    prompt = (
        f"以下はユーザーの詳細情報です:\n{user_data}\n\n"
        f"以下は推薦ユーザーの情報です:\n{similar_users_data}\n\n"
        f"この情報を基に、ユーザーの{criteria}と関係値が高い推薦ユーザーを紹介してください。"
    )

    # GPTによる応答生成
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    # 応答の表示
    return response['choices'][0]['message']['content']

# ユーザーIDに基づいてAPIを叩いてデータを取得し表示
if user_id:
    all_user_data = get_all_user()
    user_data = get_user_data(user_id)
    owner_users_data = get_owner_users(user_id)

    if user_data and owner_users_data:
        st.write("あなたの詳細情報:")
        st.dataframe(user_data)

        owner_user_ids = [item['user_id'] for item in owner_users_data]
        user_detail_list = []
        for user_id in owner_user_ids:
            data = get_user_data(user_id)
            text = data[0]["user_id"] + " " + data[0]["full_name"] + " (" + data[0]["company_name"] + ")"
            user_detail_list.append(text)
        selected_user_id = st.selectbox('名刺を所持しているユーザーを選択してください:', user_detail_list)

        similar_users_data = get_similar_users(selected_user_id)
        if similar_users_data:
            st.write("APIからの推薦ユーザー情報:")
            df_similar_users = pd.DataFrame(similar_users_data)
            st.dataframe(df_similar_users)

            # 会社に基づく推薦ボタン
            if st.button('会社に基づく推薦を取得'):
                additional_recommendations = get_additional_recommendations(user_data, similar_users_data, "会社")
                st.write("ChatGPTからのさらなる推薦 (会社):")
                st.write(additional_recommendations)

            # アドレスに基づく推薦ボタン
            if st.button('アドレスに基づく推薦を取得'):
                additional_recommendations = get_additional_recommendations(user_data, similar_users_data, "アドレス")
                st.write("ChatGPTからのさらなる推薦 (アドレス):")
                st.write(additional_recommendations)

            # ポジションに基づく推薦ボタン
            if st.button('ポジションに基づく推薦を取得'):
                additional_recommendations = get_additional_recommendations(user_data, similar_users_data, "ポジション")
                st.write("ChatGPTからのさらなる推薦 (ポジション):")
                st.write(additional_recommendations)
else:
    st.info("ユーザーIDを入力してください。")
