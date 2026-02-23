import requests
from bs4 import BeautifulSoup
import re

def get_japan_trends():
    url = "https://trends24.in/japan/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        # trends24の構造（2026年現在）：ol or ul内のli > a
        trends_section = soup.find("ol") or soup.find("ul", class_="trend-card__list")
        if not trends_section:
            return []
        trends = [li.a.text.strip() for li in trends_section.find_all("li") if li.a]
        return trends[:10]
    except Exception as e:
        print(f"Trends fetch error: {e}")
        return []

def check_shadowban(username):
    url = f"https://hisubway.online/shadowban/{username}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        # 結果は<div>や<p>に"Search Ban: Yes/No" など日本語/英語で表示
        text = soup.get_text().lower()
        search_ban = "search ban: yes" in text or "検索バン: はい" in text
        reply_deboost = "reply deboosting" in text or "リプライデブースティング" in text
        return {
            "search_ban": search_ban,
            "reply_deboost": reply_deboost,
            "likely_suppressed": search_ban or reply_deboost
        }
    except Exception as e:
        print(f"Shadowban check error: {e}")
        return {"error": str(e)}
