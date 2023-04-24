import requests
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from tqdm import tqdm
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# eprint RSS
base_url = 'https://eprint.iacr.org/rss/rss.xml'
xml_file = 'eprint.xml'
response = requests.get(base_url)

# last eprint
last_file = 'last.txt'

# Slack APIトークン
SLACK_API_TOKEN = 'xoxb-Slack API Token'
# Slackに投稿するチャンネル名を指定する
SLACK_CHANNEL = "#eprintまとめ"

# 翻訳APIのURL
# [参考：Google翻訳APIを無料で作る方法](https://qiita.com/satto_sann/items/be4177360a0bc3691fdf)
trancerate_url='Google scriptのURL'

## 英文を翻訳APIに流し込む関数
def get_summary(result):
    _params = {'text': f'{result}', 'source': 'en', 'target': 'ja'}
    r = requests.get(trancerate_url, params=_params)
    text_json = r.json()
    out_text = text_json['text']
    return out_text


with open(xml_file, "wb") as file:
    file.write(response.content)
    print("Complete DL rss file!")

with open(last_file, 'r') as file:
    lastnum = file.read()
    lastnum = lastnum.replace("/", "")
maxnum = lastnum

client = WebClient(token=SLACK_API_TOKEN)

tree = ET.parse(xml_file)
root = tree.getroot()


# itemタグの情報を抽出する
for item in tqdm(root.findall(".//item")):

    # ex) 'https://eprint.iacr.org/2023/548' => '2023548'
    eprintnum=re.findall('\d+', item.find("link").text)
    eprintnum = ''.join(eprintnum)

    # last.txtの値よりも大きい場合のみ投稿する
    if eprintnum > lastnum:

        # last.txtの値を更新する
        if maxnum < eprintnum:
            maxnum = eprintnum
        
        pub_date = item.find("pubDate").text
        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")

        title = item.find("title").text
        link = item.find("link").text
        description = item.find("description").text
        message = title+"について要約しました！ \n発行日："+ pub_date + "\n" + link + "\n" + get_summary(description)

        try:
            response = client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=message
            )
            # last.txtの値を更新する
            with open(last_file, 'w') as file:
                file.write(maxnum)
            print("Complete post message!")
        
        except SlackApiError as e:
            print(f"Error posting message: {e}")
