import requests
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from tqdm import tqdm
import random
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import openai

# eprint RSS
base_url = 'https://eprint.iacr.org/rss/rss.xml'
filename = 'eprint.xml'
response = requests.get(base_url)

with open(filename, "wb") as file:
    file.write(response.content)
    print("Complete DL rss file!")

openai.api_key = "OpenAI's API Key"
SLACK_API_TOKEN = 'xoxb-Slack API Token'
SLACK_CHANNEL = "#eprintまとめ"

def get_summary(result):
    system = """与えられた論文を3点で要約してください。"""

    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': result}
                ],
                temperature=0.25,
            )
    summary = response['choices'][0]['message']['content']
    return summary

def main():
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
            new_pub="Title:"+ title+"\nDescription:"+ description
            message = title+"について要約しました！ \n発行日："+ pub_date + "\n" + link + "\n" + get_summary(new_pub)

            try:
                response = client.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=message
                )
            except SlackApiError as e:
                print(f"Error posting message: {e}")

if __name__ == "__main__":
    main()
    