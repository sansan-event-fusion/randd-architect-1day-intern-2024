import os
import requests
import streamlit as st

import openai

openai.api_key = os.environ.get("OPENAP_APIKEY")


def get_additional_recommendations(user_data, similar_users_data):
    # プロンプトを生成する
    prompt = (
        f"以下は私のユーザーの詳細情報です:\n{user_data}\n\n"
        f"以下は推薦ユーザーの情報です:\n{similar_users_data}\n\n"
        "この情報を基に、すべての推薦ユーザーに営業をかけるときはどうすればよいか？ユーザーにマッチした攻略方法を，"
        "それぞれのユーザーごとに提示してください．PMBOKのステークホルダーマネジメントを意識してください．"
    )

    # GPTによる応答生成
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].text

    except openai.error.RateLimitError:
        return "APIクォータを超えました。プランと請求情報を確認してください。"


# タイトル


st.title("営業コンサルくん")

# ユーザーIDの入力欄を作成する
user_id = st.text_input("あなたのユーザーIDを入力してください")

# 入力されたユーザーIDでAPIを叩いてデータを取得
if user_id:
    # ダミーのAPIエンドポイント（実際のAPIエンドポイントに置き換えてください）
    response = requests.get(f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}", timeout=10)
    
    if response.status_code == 200:
        user_data_list = response.json()
        
        if user_data_list:
            user_data = user_data_list[0]  # 最初のユーザーデータを取得

            # データをカード形式で表示する
            st.markdown(
                f"""
                ### あなたのカード
                <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin:10px 0;">
                    <h2>{user_data['full_name']}</h2>
                    <p><strong>役職:</strong> {user_data['position']}</p>
                    <p><strong>会社名:</strong> {user_data['company_name']}</p>
                    <p><strong>住所:</strong> {user_data['address']}</p>
                    <p><strong>電話番号:</strong> {user_data['phone_number']}</p>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.error("ユーザーデータが見つかりませんでした。")
    else:
        st.error("データの取得に失敗しました。")
    
    response = requests.get(f"https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/owner_users/{user_id}", timeout=10)
    user_have_cards = response.json()
    
    # APIエンドポイントのベースURL
    base_url = f"https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{{}}/similar_top10_users"

    similar_users_list = []

    # 各ユーザーに対して類似するユーザーを取得し、出力する
    for user in user_have_cards:
        user_id_value = user["user_id"]
        url = base_url.format(user_id_value)
        
        # APIリクエストを送信
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            similar_users = response.json()
            similar_users_list += similar_users
        else:
            st.error(f"ユーザー {user_id_value} の類似するユーザー情報の取得に失敗しました。")
    
    filtered_data = [d for d in similar_users_list if '千葉県' in d['address']]
    filtered_data = [d for d in filtered_data if d['user_id'] != str(user_id)]
    
    filtered_data = filtered_data[:4]
    
    # filtered_dataをカード形式で一気に表示
    st.markdown(
        f"""
        ### あなたの取引先と似ているユーザー
        """, unsafe_allow_html=True
    )
    for data in filtered_data:
        st.markdown(
            f"""
            <div style="border:1px solid #ddd; border-radius:10px; padding:10px; margin:10px 0;">
                <h2>{data['full_name']}</h2>
                <p><strong>役職:</strong> {data['position']}</p>
                <p><strong>会社名:</strong> {data['company_name']}</p>
                <p><strong>住所:</strong> {data['address']}</p>
                <p><strong>電話番号:</strong> {data['phone_number']}</p>
            </div>
            """, unsafe_allow_html=True
        )
    
    # 類似ユーザーデータを使って追加の推薦を取得
    recommendations = get_additional_recommendations(user_data, filtered_data)

    # 推薦結果を吹き出し形式で表示
    st.markdown(f"### AIによる攻略方法アドバイス\n{recommendations}")
