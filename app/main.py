import pandas as pd
import requests
import streamlit as st


st.title("名刺交換表示")
url = "https://circuit-trial.stg.rd.ds.sansan.com/api/"

# session_stateにcardsがない場合はcardsを追加
if "cards" not in st.session_state:
    st_cards = requests.get(url + "cards/?offset=0&limit=2000", timeout=(3.0, 7.5))
    st.session_state.cards = st_cards.json()
    st_cards_json = {}
    for card in st_cards.json():
        st_cards_json[card["user_id"]] = card
    st.session_state.cards_json = st_cards_json
    st.session_state.cards_df = pd.DataFrame(st_cards.json())
if "contacts" not in st.session_state:
    st_contacts = requests.get(url + "contacts/?offset=0&limit=99439", timeout=(3.0, 7.5))
    st.session_state.contacts = st_contacts.json()
    st.session_state.contacts_df = pd.DataFrame(st_contacts.json())

cards = st.session_state.cards
contacts = st.session_state.contacts
cards_json = st.session_state.cards_json
cards_df = st.session_state.cards_df
contacts_df = st.session_state.contacts_df

with st.expander("ログイン情報を入力して下さい"):
    user_id = st.text_input("ユーザーID")
    phone_number = st.text_input("電話番号")

if (
    user_id in cards_json
    and user_id != ""
    and phone_number != ""
    and phone_number == cards_json[user_id]["phone_number"]
):
    # 会社内の名刺を表示 company_idが一致するものを表示
    same_company_cards = cards_df[cards_df["company_id"] == cards_json[user_id]["company_id"]]
    # 会社内の所有する名刺を表示
    same_company_contacts = contacts_df[contacts_df["owner_user_id"].isin(same_company_cards["user_id"])]
    for _, row in same_company_contacts.iterrows():
        user = cards_json[row["user_id"]]
        with st.popover(f'{user["full_name"]}様 [{user["company_name"]}]'):
            st.write(f'{user["company_name"]}　{user["position"]}')
            st.write(f'住所:{user["address"]}, 　電話番号:{user["phone_number"]}')
            st.write(f'{cards_json[row["owner_user_id"]]["full_name"]}が取得しました。')
elif user_id != "" and phone_number != "":
    st.write("ログイン情報が間違っています")
