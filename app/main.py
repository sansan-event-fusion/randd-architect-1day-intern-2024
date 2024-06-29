import pandas as pd
import requests
import streamlit as st
from module import format_trans_table

mst_url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=2000"
mst_r = requests.get(mst_url, timeout=10)
mst_df = pd.DataFrame(mst_r.json())

company_dict = (
    mst_df[["company_id", "company_name"]].drop_duplicates().set_index("company_id")["company_name"].to_dict()
)


def get_transactions(company_id):
    trans_url = (
        f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_companies/{company_id}?offset=0&limit=1000"
    )
    trans_r = requests.get(trans_url, timeout=10)
    trans_df = pd.DataFrame(trans_r.json())
    return format_trans_table(trans_df, mst_df)


# タイトル
st.title("営業成果")

company_name = st.selectbox("会社名", list(company_dict.values()))
company_id = next(k for k, v in company_dict.items() if v == company_name)
st.write(f"選択中の会社: {company_name}, id: {company_id}")

submit = st.button("取引履歴を取得")

if submit and company_id:
    try:
        trans_df = get_transactions(company_id)
        st.dataframe(trans_df, use_container_width=True)
    except requests.exceptions.RequestException as e:
        st.write(f"リクエストエラーが発生しました: {e}")
    except ValueError as e:
        st.write(f"データ処理エラーが発生しました: {e}")

if submit and trans_df is not None:
    st.header("summary")
    summary = (
        trans_df.groupby("担当者")
        .agg({"取引先": "count", "ポイント": "mean"})
        .sort_values("ポイント", ascending=False)
    )

    for idx, row in summary.iterrows():
        st.metric(
            label=idx,
            value=f"{int(row['取引先'])}回の交換",
            delta=f"{round(row['ポイント'], 1)} point",
        )
