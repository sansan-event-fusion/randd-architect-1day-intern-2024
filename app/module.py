positions = {
    7: ["部長", "技術部長", "営業部長"],
    6: ["次長", "技術次長", "営業次長", "課長", "技術課長", "営業課長"],
    5: ["係長", "技術係長", "営業係長", "主任", "技術主任", "営業主任"],
    4: [
        "プロダクトマネージャー",
        "プロジェクトマネージャー",
        "アカウントマネージャー",
        "カスタマーサポートマネージャー",
        "アシスタントマネージャー",
    ],
    3: ["シニアアナリスト", "リードエンジニア"],
    2: ["一般社員", "新入社員"],
    1: ["アナリスト", "ジュニアアナリスト", "ソフトウェアエンジニア", "システムエンジニア", "データサイエンティスト"],
}

position_to_rank = {position: rank for rank, positions in positions.items() for position in positions}


def get_position_rank(position):
    return position_to_rank.get(position)


def compare_positions(position1, position2):
    rank1 = get_position_rank(position1)
    rank2 = get_position_rank(position2)

    if rank1 is None or rank2 is None:
        msg = f"Invalid position: {position1}, {position2}"
        raise ValueError(msg)

    return rank1 - rank2


def format_trans_table(trans_df, mst_df):
    # trans_dfの_owner_user_id列をmst_dfの名前に変換
    trans_df["score"] = trans_df.apply(
        lambda x: compare_positions(
            mst_df[mst_df["user_id"] == x["owner_user_id"]].position.to_numpy()[0],
            mst_df[mst_df["user_id"] == x["user_id"]].position.to_numpy()[0],
        ),
        axis=1,
    )

    trans_df["owner_user_id"] = trans_df["owner_user_id"].apply(
        lambda x: mst_df[mst_df["user_id"] == x].iloc[0]["full_name"]
    )
    trans_df["user_id"] = trans_df["user_id"].apply(lambda x: mst_df[mst_df["user_id"] == x].iloc[0]["full_name"])

    # 使うcolumnsだけに絞り，列名を日本語に変換
    use_cols = {"owner_user_id": "担当者", "user_id": "取引先", "score": "ポイント"}
    trans_df = trans_df.rename(columns=use_cols)
    return trans_df[use_cols.values()]
