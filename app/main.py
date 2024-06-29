import re
from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# API取得
def get_employee_contact_count(user_id):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{user_id}/count"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    return 0


def get_company_contact_count(company_id):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_companies/{company_id}/count"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    return 0


def get_contact_history(user_id):
    url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{user_id}"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        return response.json()
    return []


def classify_company(company_name):
    for industry, pattern in patterns.items():
        if re.search(pattern, company_name):
            return industry
    return "その他"


def aggregate_by_time_interval(contact_history, time_interval):
    if not contact_history:
        return pd.DataFrame(columns=[time_interval, "count"])

    data = pd.DataFrame(contact_history)
    data["created_at"] = pd.to_datetime(data["created_at"])

    if time_interval == "year":
        data[time_interval] = data["created_at"].dt.year
    elif time_interval == "month":
        data[time_interval] = data["created_at"].dt.to_period("M").astype(str)
    elif time_interval == "week":
        data[time_interval] = (
            data["created_at"].apply(lambda x: x - timedelta(days=x.weekday())).dt.strftime("%Y-%m-%d")
        )

    aggregated_counts = data.groupby(time_interval).size().reset_index(name="count")
    return aggregated_counts


url = "https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=1000"
response = requests.get(url, timeout=10)
data = response.json()
data = pd.DataFrame(data)

# 業種ごとの正規表現パターン
patterns = {
    "運輸業": r"運輸|運送",
    "情報・通信業": r"通信|情報",
    "水産業": r"水産",
    "建設業": r"建設",
    "鉱業": r"鉱業",
    "農林業": r"農林",
    "保険業": r"保険",
    "印刷業": r"印刷",
    "食品業": r"食品",
    "ガス業": r"ガス",
}

data["Industry"] = data["company_name"].apply(classify_company)

selected_industry = st.selectbox("業種を選択してください", list(patterns.keys()))
filtered_companies = data[data["Industry"] == selected_industry]["company_name"].unique()

data_rows = []

for company_name in filtered_companies:
    company_id = data[data["company_name"] == company_name]["company_id"].iloc[0]
    contact_count = get_company_contact_count(company_id)
    data_rows.append({"company": company_name, "contact_sum": contact_count})

industry_df = pd.DataFrame(data_rows)

prefectures = []


def extract_prefecture(address):
    pattern = r"(\S+?[都道府県])"
    match = re.search(pattern, address)
    if match:
        return match.group(1)
    return "Unknown"


for company_name in filtered_companies:
    unique_address = data[data["company_name"] == company_name]["address"].unique()
    if len(unique_address) > 0:
        prefecture = extract_prefecture(unique_address[0])
        prefectures.append(prefecture)

industry_df["address"] = prefectures

industry_df = industry_df.sort_values(by="contact_sum", ascending=False)
st.dataframe(industry_df)

selected_company = st.selectbox("会社名を選択してください", filtered_companies)

st.write(f"### {selected_company} の従業員情報")

company_data = data[data["company_name"] == selected_company][["position", "full_name", "phone_number", "user_id"]]
company_data["contact_sum"] = company_data["user_id"].apply(get_employee_contact_count)

company_data = company_data.sort_values(by="contact_sum", ascending=False)

st.dataframe(company_data.drop(columns=["user_id"]))


time_intervals = ["year", "month", "week"]
selected_interval = st.radio("時間間隔を選択してください", time_intervals)

fig = go.Figure()

for _, row in company_data.iterrows():
    user_id = row["user_id"]
    full_name = row["full_name"]
    contact_history = get_contact_history(user_id)
    aggregated_counts = aggregate_by_time_interval(contact_history, selected_interval)

    if not aggregated_counts.empty:
        # Add trace for each employee with name as label and color
        fig.add_trace(
            go.Scatter(
                x=aggregated_counts[selected_interval],
                y=aggregated_counts["count"],
                mode="lines+markers",
                name=full_name,
            )
        )
fig.update_layout(
    title=f"従業員ごとの{selected_interval}ごとの履歴件数",
    xaxis_title=selected_interval.capitalize() if selected_interval else "Default Title",
    yaxis_title="連絡履歴件数",
    hovermode="x",
    legend_title="従業員名",
)

# グラフ表示
st.plotly_chart(fig)
