import networkx as nx
import streamlit as st
import requests


st.set_page_config(page_title="Optimal Contact Path")
# タイトル
st.title("人脈検索アプリ")
# ユーザー名入力
user_name = st.text_input("あなたの名前を入力してください")
target_name = st.text_input("連絡を取りたい人の名前を入力してください")


def fetch_all_contacts():
    """全ユーザーの連絡履歴を取得"""
    contacts = []
    offset = 0
    limit = 10000
    while True:
        url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/contacts/?offset={offset}&limit={limit}'
        response = requests.get(url)
        response.raise_for_status()
        batch = response.json()
        contacts.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return contacts


# CSSスタイルを追加して名刺をカード形式にする
st.markdown("""
    <style>
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #ddd;
        position: relative;
    }
    .card h4 {
        margin: 0;
        padding-bottom: 10px;
        border-bottom: 1px solid #ddd;
    }
    .card p {
        margin: 5px 0;
    }
    .arrow {
        width: 0;
        height: 0;
        border-left: 20px solid transparent;
        border-right: 20px solid transparent;
        border-top: 20px solid #ddd;
        margin: 20px auto;
    }
    </style>
""", unsafe_allow_html=True)


# 全ての名刺情報を取得する関数
def fetch_all_cards():
    cards = []
    offset = 0
    limit = 10000
    while True:
        url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset={offset}&limit={limit}'
        response = requests.get(url)
        response.raise_for_status()
        batch = response.json()
        cards.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return cards


# 名刺データの取得
try:
    cards = fetch_all_cards()
except requests.exceptions.RequestException as e:
    st.error(f"データ取得中にエラーが発生しました: {e}")
    cards = []


def fetch_card(user_id):
    """指定されたユーザーIDの名刺データを取得"""
    url = f'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/{user_id}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()[0]  # リストの最初の要素を返す


def build_graph(contacts):
    """連絡履歴データからグラフを作成"""
    G = nx.Graph()
    for contact in contacts:
        owner_id = contact['owner_user_id']
        user_id = contact['user_id']
        # 類似度を重みとしてエッジを追加
        similarity = 1.0  # 類似度の計算方法に応じて適切に設定
        G.add_edge(owner_id, user_id, weight=1/similarity)
    return G


if st.button("検索"):
    if user_name and target_name:
        try:
            # 全ての連絡履歴を取得
            contacts = fetch_all_contacts()

            # 名前からユーザーIDを検索
            user_ids = {card['full_name']: card['user_id'] for card in cards}
            user_id = user_ids.get(user_name)
            target_id = user_ids.get(target_name)

            if not user_id or not target_id:
                st.error("指定された名前のユーザーが見つかりませんでした")
            else:
                # グラフの作成
                G = build_graph(contacts)

                # 最短経路の計算
                if nx.has_path(G, user_id, target_id):
                    paths = list(nx.all_shortest_paths(G, source=user_id, target=target_id, weight='weight'))
                    
                    # トグルを用いた経路の表示
                    for i, path in enumerate(paths[:3]):
                        with st.expander(f"{i+1}番目に最適な連絡方法"):
                            # st.success(f"経路: {' -> '.join(path)}")
                            for uid in path:
                                try:
                                    card = fetch_card(uid)
                                    st.markdown(f"""
                                        <div class="card">
                                            <h4>{card.get('full_name', '不明')}</h4>
                                            <p><b>User ID:</b> {card.get('user_id', '不明')}</p>
                                            <p><b>Position:</b> {card.get('position', '不明')}</p>
                                            <p><b>Company:</b> {card.get('company_name', '不明')}</p>
                                            <p><b>Address:</b> {card.get('address', '不明')}</p>
                                            <p><b>Phone:</b> {card.get('phone_number', '不明')}</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    if uid != path[-1]:
                                        st.markdown('<div class="arrow"></div>', unsafe_allow_html=True)
                                except Exception as e:
                                    st.error(f"ユーザーID {uid} の名刺データ取得中にエラーが発生しました: {e}")
                else:
                    st.error("指定されたユーザー間に経路が存在しません")

        except requests.exceptions.RequestException as e:
            st.error(f"データ取得中にエラーが発生しました: {e}")
    else:
        st.warning("両方の名前を入力してください")
