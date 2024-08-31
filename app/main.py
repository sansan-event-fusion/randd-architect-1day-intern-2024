from pathlib import Path

import pandas as pd
import streamlit as st
import requests
from datetime import datetime, timedelta

# API_cards
API_cards_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=100"

# API_contacts
API_contacts_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/?offset=0&limit=100"

#API_contacts_users
API_contacts_users_URL = "https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/4578252120?offset=0&limit=100"

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

# APIから名刺交換日時を取得
@st.cache_data
def fetch_exchange_history_date():
    try:
        response = requests.get(f"{API_contacts_users_URL}")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"名刺交換履歴の取得に失敗しました: {e}")
        return pd.DataFrame()

    
# 名刺情報の表示
st.subheader('名刺情報')
cards_df = fetch_business_cards()
if not cards_df.empty:
    st.dataframe(cards_df)
else:
    st.write("名刺情報がありません。")

# 名刺交換履歴の表示
st.subheader('名刺交換履歴')
history_df = fetch_business_contacts()
if not history_df.empty:
    st.dataframe(history_df)
else:
    st.write("名刺交換履歴がありません。")

# 指定したユーザーの名刺交換情報の表示
st.subheader('指定したユーザーの名刺交換情報')
history_df = fetch_exchange_history_date()
if not history_df.empty:
    st.dataframe(history_df)
else:
    st.write("名刺交換情報がありません。")


# 元ファイル
# path = Path(__file__).parent / "dummy_data.csv"
# df_dummy = pd.read_csv(path.as_uri(), dtype=str)

# st.dataframe(df_dummy)
