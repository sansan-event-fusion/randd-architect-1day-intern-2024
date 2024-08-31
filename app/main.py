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

# list contact history by owner company in 2022
contacts_by_owner_company_df = fetch_data_json('https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_companies/8256438734?start_date=2022-01-01T00%3A00%3A00Z&end_date=2022-12-31T00%3A00%3A00Z')

owner_user_ids = contacts_by_owner_company_df['owner_user_id'].unique()

contact_count_list = []

for owner_user_id in owner_user_ids:
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{owner_user_id}/count?start_date=2022-01-01T00%3A00%3A00Z&end_date=2022-12-31T00%3A00%3A00Z"
    contact_count_by_user = fetch_data_number(url)
    contact_count_by_user_data = {
        "owner_user_id": owner_user_id,
        "contact_count": contact_count_by_user,
    }
    contact_count_list.append(contact_count_by_user_data)

print(contact_count_list)
contact_count_df = pd.DataFrame(contact_count_list)

st.title("Contact History Count")
st.dataframe(contact_count_df)

