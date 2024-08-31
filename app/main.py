import pandas as pd
import requests
import streamlit as st

# API_cards
API_cards_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=100"

# API_contacts
API_contacts_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/?offset=0&limit=100"

# API_contacts_users
API_contacts_users_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users"

# タイトル
st.title("Reconnect Card")


# APIから名刺情報を取得
@st.cache_data
def fetch_business_cards():
    try:
        response = requests.get(f"{API_cards_URL}")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"名刺情報の取得に失敗しました: {e}")
        return pd.DataFrame()


# APIから名刺交換履歴を取得
@st.cache_data
def fetch_business_contacts():
    try:
        response = requests.get(f"{API_contacts_URL}")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"名刺交換履歴の取得に失敗しました: {e}")
        return pd.DataFrame()


# APIから特定ユーザーの名刺交換履歴を取得
@st.cache_data
def fetch_exchange_history_date(owner_user_id):  # user_id を引数として受け取る
    try:
        # URLの形式はAPI仕様に合わせて修正してください
        response = requests.get(f"{API_contacts_users_URL}/{owner_user_id}?offset=0&limit=100")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"名刺交換履歴の取得に失敗しました: {e}")
        return pd.DataFrame()


# 名刺情報の表示
st.subheader("名刺情報")
cards_df = fetch_business_cards()
if not cards_df.empty:
    # フルネームのリストを作成して選択ボックスに表示
    selected_name = st.selectbox("ユーザーを選択", cards_df["full_name"])

    # 選択されたユーザーの情報を取得
    selected_user = cards_df[cards_df["full_name"] == selected_name]
    selected_user_id = selected_user.iloc[0]["user_id"]

    # ボタンをクリックして名刺交換履歴を取得
    if st.button("このユーザーの名刺交換履歴を表示"):
        history_df = fetch_exchange_history_date(selected_user_id)
        if not history_df.empty:
            st.subheader(f"{selected_name}の名刺交換履歴")
            st.dataframe(history_df)
        else:
            st.write("このユーザーの名刺交換履歴がありません。")
else:
    st.write("名刺情報がありません。")
