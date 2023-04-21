import requests
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from tqdm import tqdm
import random
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# eprint RSS
base_url = 'https://eprint.iacr.org/rss/rss.xml'
filename = 'eprint.xml'
response = requests.get(base_url)

with open(filename, "wb") as file:
    file.write(response.content)
    print("Complete DL rss file!")

# Slack APIトークン
SLACK_API_TOKEN = 'xoxb-Slack API Token'
# Slackに投稿するチャンネル名を指定する
SLACK_CHANNEL = "#eprintまとめ"

# 翻訳APIのURL
# [参考：Google翻訳APIを無料で作る方法](https://qiita.com/satto_sann/items/be4177360a0bc3691fdf)
trancerate_url='Google scriptのURL'

def get_summary(result):
    _params = {'text': f'{result}', 'source': 'en', 'target': 'ja'}
    r = requests.get(trancerate_url, params=_params)
    text_json = r.json()
    out_text = text_json['text']
    return out_text



now = datetime.now()
yesterday = now - timedelta(days=1)
current_date = yesterday.strftime("%Y-%m-%d")

client = WebClient(token=SLACK_API_TOKEN)

xml_file = "eprint.xml"

tree = ET.parse(xml_file)
root = tree.getroot()


# itemタグの情報を抽出する
for item in tqdm(root.findall(".//item")):
    pub_date = item.find("pubDate").text
    pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")

    # 今日の日付と一致する場合にのみ情報を表示する
    if pub_date == current_date:
        title = item.find("title").text
        link = item.find("link").text
        description = item.find("description").text
        message = title+"について要約しました！ \n発行日："+ pub_date + "\n" + link + "\n" + get_summary(description)

        try:
            response = client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=message
            )
        except SlackApiError as e:
            print(f"Error posting message: {e}")
