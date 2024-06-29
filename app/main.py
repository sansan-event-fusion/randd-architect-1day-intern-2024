from pathlib import Path
import requests
import pandas as pd

import pandas as pd
import streamlit as st

from module import compare_positions, format_trans_table

company_id = None
trans_df = None

mst_url = 'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=2000'
mst_r = requests.get(mst_url)
mst_df = pd.DataFrame(mst_r.json())

company_dict = mst_df[["company_id", "company_name"]].drop_duplicates().set_index("company_id")["company_name"].to_dict()

def get_transactions(company_id):
    trans_url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_companies/{company_id}?offset=0&limit=1000'
    trans_r = requests.get(trans_url)
    trans_df = pd.DataFrame(trans_r.json())
    return format_trans_table(trans_df, mst_df)


# タイトル
st.title("人事評価")

company_name = st.selectbox("会社名", list(company_dict.values()))
company_id = [k for k, v in company_dict.items() if v == company_name][0]
st.write(f"選択中の会社: {company_name}, id: {company_id}")

submit = st.button("取引履歴を取得")
if submit:
    if company_id:
        try:
            trans_df = get_transactions(company_id)
            st.table(trans_df)
        except Exception as e:
            st.write(f"エラーが発生しました: {e}")

# if submit:
#     if company_id is not None and trans_df is not None:
#         owner = trans_df["owner_user_id"]
#         user = trans_df["user_id"]

#         owner_job = mst_df[mst_df["user_id"] == owner].position.values[0]
#         user_job = mst_df[mst_df["user_id"] == user].position.values[0]
#         st.write(compare_positions(owner_job, user_job))
