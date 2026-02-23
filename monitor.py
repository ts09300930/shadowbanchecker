from datetime import datetime
from utils.scraper import check_shadowban
from utils.notifier import send_line_notify
import json
import os

# 複数アカウントJSON読み込み
ACCOUNTS_FILE = "config/monitored_accounts.json"
if os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        monitored_accounts = json.load(f)
else:
    monitored_accounts = []

messages = []
for username in monitored_accounts:
    result = check_shadowban(username)
    status = "抑制疑いあり" if result.get("likely_suppressed") else "正常"
    messages.append(f"@{username}: {status} (Search Ban: {result.get('search_ban')})")

full_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M JST')}] 複数アカウント監視結果\n" + "\n".join(messages)
send_line_notify(full_msg)
