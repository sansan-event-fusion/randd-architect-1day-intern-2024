import streamlit as st
import requests
import pandas as pd
import openai
from dotenv import load_dotenv
import os

# 環境変数をロード
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv('OPENAI_API_KEY')

# タイトル
st.title("営業先推薦アプリ")

# user_idの入力を受け取る部分
user_id = st.text_input("ユーザーIDを入力してください:")

# APIからユーザーのデータを取得する関数
def get_user_data(user_id):
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        return None

# APIから推薦データを取得する関数
def get_similar_users(user_id):
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}/similar_top10_users'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code}")
        return None

# OpenAI APIを利用してさらなる推薦を取得する関数
def get_additional_recommendations(user_data, similar_users_data):
    # プロンプトを生成する
    prompt = (
        f"以下はユーザーの詳細情報です:\n{user_data}\n\n"
        f"以下は推薦ユーザーの情報です:\n{similar_users_data}\n\n"
        "この情報を基に、ユーザーの会社と関係値が高い推薦ユーザーを紹介してください。"
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
    user_data = get_user_data(user_id)
    if user_data:
        st.write("ユーザーの詳細情報:")
        st.dataframe(user_data)

    similar_users_data = get_similar_users(user_id)
    if similar_users_data:
        st.write("APIからの推薦ユーザー情報:")
        df_similar_users = pd.DataFrame(similar_users_data)
        st.dataframe(df_similar_users)

        additional_recommendations = get_additional_recommendations(user_data, similar_users_data)
        st.write("ChatGPTからのさらなる推薦:")
        st.write(additional_recommendations)
else:
    st.info("ユーザーIDを入力してください。")
