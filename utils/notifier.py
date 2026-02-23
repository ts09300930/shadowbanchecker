import requests
import os

def send_line_notify(message):
    token = os.getenv("LINE_NOTIFY_TOKEN")
    if not token:
        print("LINE_NOTIFY_TOKEN が設定されていません。通知をスキップ。")
        return
    
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": message}
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        print("LINE通知送信成功")
    except Exception as e:
        print(f"LINE通知エラー: {e}")
