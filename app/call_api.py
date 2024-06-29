import requests
import csv
import re
from collections import defaultdict

def get_cards():
    url = 'https://circuit-trial.stg.rd.ds.sansan.com/api/cards/?offset=0&limit=100'
    response = requests.get(url)
    return response.json()

def count_companies_by_prefecture(data):
    prefecture_pattern = re.compile(r'^(北海道|青森県|岩手県|宮城県|秋田県|山形県|福島県|茨城県|栃木県|群馬県|埼玉県|千葉県|東京都|神奈川県|新潟県|富山県|石川県|福井県|山梨県|長野県|岐阜県|静岡県|愛知県|三重県|滋賀県|京都府|大阪府|兵庫県|奈良県|和歌山県|鳥取県|島根県|岡山県|広島県|山口県|徳島県|香川県|愛媛県|高知県|福岡県|佐賀県|長崎県|熊本県|大分県|宮崎県|鹿児島県|沖縄県)')
    company_count_by_prefecture = defaultdict(int)
    
    for item in data:
        address = item['address']
        match = prefecture_pattern.match(address)
        if match:
            prefecture = match.group(1)
            company_count_by_prefecture[prefecture] += 1
    
    result_dict = dict(company_count_by_prefecture)

def organize_data_by_prefecture(data):
    prefecture_pattern = re.compile(r'^(北海道|青森県|岩手県|宮城県|秋田県|山形県|福島県|茨城県|栃木県|群馬県|埼玉県|千葉県|東京都|神奈川県|新潟県|富山県|石川県|福井県|山梨県|長野県|岐阜県|静岡県|愛知県|三重県|滋賀県|京都府|大阪府|兵庫県|奈良県|和歌山県|鳥取県|島根県|岡山県|広島県|山口県|徳島県|香川県|愛媛県|高知県|福岡県|佐賀県|長崎県|熊本県|大分県|宮崎県|鹿児島県|沖縄県)')
    data_by_prefecture = defaultdict(list)

    for item in data:
        address = item['address']
        match = prefecture_pattern.match(address)
        if match:
            prefecture = match.group(1)
            company_info = {
                '氏名': item['full_name'],
                '役職': item['position'],
                '会社名': item['company_name'],
                '住所': item['address'],
                '電話番号': item['phone_number']
            }
            data_by_prefecture[prefecture].append(company_info)
    return dict(data_by_prefecture)


data = get_cards()
#print(data)
result = count_companies_by_prefecture(data)
print(organize_data_by_prefecture(data))

