import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from utils.scraper import get_japan_trends, check_shadowban
from utils.risky_words import RISKY_WORDS
import re

# ローカル開発時のみ .env を読み込む（Streamlit CloudではSecrets使用）
if os.path.exists(".env"):
    load_dotenv()

client = OpenAI(api_key=os.getenv("GROK_API_KEY"), base_url="https://api.x.ai/v1")

# 複数アカウントJSON読み込み
ACCOUNTS_FILE = "config/monitored_accounts.json"
if os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        monitored_accounts = json.load(f)
else:
    monitored_accounts = []
    st.warning("monitored_accounts.json が存在しません。config/フォルダに作成してください。")

# 履歴JSON
HISTORY_FILE = "utils/history.json"
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = []

def save_history(entry):
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def has_risky_word(text):
    for pattern in RISKY_WORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

st.title("R18ツイート最適化ツール（話題入り支援）")

tab1, tab2, tab3 = st.tabs(["書き換え＆判定", "トレンドチェック", "履歴・分析"])

with tab1:
    original = st.text_area("元のツイート")
    if st.button("書き換え＆OK判定"):
        if original:
            prompt = f"""このエロティックなツイートを、ほぼ同じ意味と興奮させるニュアンス（おじさんをむらむらさせる形）を保ちつつ、Twitterのシャドウバンに引っかかりやすい露骨な文言を同義語や婉曲的な自然な表現に置き換えてください。センシティブ単語を徹底的に避け、魅力的に：{original}"""
            resp = client.chat.completions.create(
                model="grok-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.8
            )
            rewritten = resp.choices[0].message.content.strip()
            st.subheader("提案")
            st.write(rewritten)
            
            is_ok = not has_risky_word(rewritten)
            if is_ok:
                st.success("OK：高リスク単語なし。引っかかりにくい可能性が高いです。")
            else:
                st.warning("注意：リスク単語残存。調整推奨。")
            
            save_history({
                "time": datetime.now().isoformat(),
                "original": original,
                "rewritten": rewritten,
                "ok": is_ok
            })

with tab2:
    if st.button("現在トレンド取得＆一致チェック"):
        trends = get_japan_trends()
        if trends:
            st.write("日本トップトレンド（最新）:")
            for i, t in enumerate(trends, 1):
                st.write(f"{i}. {t}")
            
            # Grokでキーワード抽出（オプション拡張可能）
            if original:
                extract_prompt = f"このツイートからトレンドに合いそうなキーワード/ハッシュタグを3つ抽出：{original}"
                resp = client.chat.completions.create(
                    model="grok-4",
                    messages=[{"role": "user", "content": extract_prompt}],
                    max_tokens=50
                )
                keywords = resp.choices[0].message.content.strip()
                st.write(f"抽出キーワード: {keywords}")
                # トレンドマッチング（簡易）
                matches = [t for t in trends if any(k in t for k in keywords.split())]
                if matches:
                    st.success(f"一致トレンド: {', '.join(matches)}")
                else:
                    st.warning("トレンド一致なし。キーワード調整を検討。")
        else:
            st.error("トレンド取得失敗。後ほど再試行を。")

    st.subheader("複数アカウント可視性チェック")
    if monitored_accounts:
        results = {}
        for username in monitored_accounts:
            results[username] = check_shadowban(username)
        
        for username, res in results.items():
            st.write(f"@{username}:")
            st.json(res)
            if res.get("likely_suppressed"):
                st.error("Search Banまたは抑制疑いあり → 話題の欄表示リスク高")
            else:
                st.success("抑制兆候なし")
    else:
        st.info("監視アカウントがありません。")

with tab3:
    st.subheader("履歴")
    if history:
        for entry in reversed(history[-10:]):
            st.markdown(f"**{entry['time']}** OK:{entry['ok']}")
            st.write(f"元: {entry['original'][:100]}...")
            st.write(f"提: {entry['rewritten'][:100]}...")
    else:
        st.info("履歴なし")

    if st.button("履歴分析（Grok）"):
        if history:
            hist_text = json.dumps(history[-5:], ensure_ascii=False)
            anal_prompt = f"以下の履歴から、話題入りしやすかった表現パターンを分析：{hist_text}"
            resp = client.chat.completions.create(
                model="grok-4",
                messages=[{"role": "user", "content": anal_prompt}],
                max_tokens=150
            )
            analysis = resp.choices[0].message.content.strip()
            st.write("分析結果:")
            st.write(analysis)
