from pathlib import Path

import pandas as pd
import streamlit as st
import requests

# タイトル
# st.title("サンプルアプリ")

# path = Path(__file__).parent / "dummy_data.csv"
# df_dummy = pd.read_csv(path.as_uri(), dtype=str)

# st.dataframe(df_dummy)

def fetch_data_json(url):
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    return df

def fetch_data_number(url):
    response = requests.get(url)
    data = response.json()
    return data

def show_data(year):
    # list contact history by owner company in 2022
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_companies/8256438734?start_date={year}-01-01T00%3A00%3A00Z&end_date={year}-12-31T00%3A00%3A00Z"
    contacts_by_owner_company_df = fetch_data_json(url)

    owner_user_ids = contacts_by_owner_company_df['owner_user_id'].unique()

    contact_count_list = []

    for owner_user_id in owner_user_ids:
        url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{owner_user_id}/count?start_date={year}-01-01T00%3A00%3A00Z&end_date={year}-12-31T00%3A00%3A00Z"
        contact_count_by_user = fetch_data_number(url)

        url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{owner_user_id}"
        user_card_df = fetch_data_json(url)
        full_name = user_card_df['full_name'].iloc[0]
        print(full_name)
        position = user_card_df["position"].iloc[0]
        print(position)

        contact_count_by_user_data = {
            "owner_user_id": owner_user_id,
            "full_name": full_name,
            "position": position,
            "contact_count": contact_count_by_user,
        }
        contact_count_list.append(contact_count_by_user_data)

    contact_count_df = pd.DataFrame(contact_count_list)
    contact_count_df = contact_count_df.sort_values(by=['contact_count'], ascending=[False])

    st.write(f"year: {year}")
    st.dataframe(contact_count_df)


st.title(f"1年以内の名刺交換回数ランキング")

with st.form(key='year_form'):
    year = st.text_input(label='Year')
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    show_data(year)