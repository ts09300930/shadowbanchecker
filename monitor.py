# 簡易版：アカウント抑制チェック → LINE通知
import requests
from utils.scraper import check_shadowban
from utils.notifier import send_line_notify  # LINE Notify関数を別途定義

username = "your_username"  # 環境変数化推奨
result = check_shadowban(username)

msg = f"[{datetime.now()}] {username} Shadowbanチェック\n"
msg += f"Search Ban: {result.get('search_ban')}\n"
msg += f"抑制疑い: {result.get('likely_suppressed')}\n"

send_line_notify(msg)
