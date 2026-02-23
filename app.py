import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from utils.scraper import get_japan_trends, check_shadowban
from utils.risky_words import RISKY_WORDS  # 正規表現リストを別ファイルに
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("GROK_API_KEY"), base_url="https://api.x.ai/v1")
TARGET_USERNAME = os.getenv("TARGET_USERNAME", "your_username")

# 履歴ロード
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

# 高リスクワードチェック関数（utils/risky_words.pyに定義推奨）
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
            
            # Grokでキーワード抽出
            extract_prompt = f"このツイートからトレンドに合いそうなキーワード/ハッシュタグを3つ抽出：{original if 'original' in locals() else '（ツイート未入力）'}"
            # ...（省略：API呼び出しで抽出後、マッチング表示）
        else:
            st.error("トレンド取得失敗。後ほど再試行を。")

    username = st.text_input("監視ユーザー名（@なし）", value=TARGET_USERNAME)
    if st.button("可視性チェック"):
        result = check_shadowban(username)
        st.json(result)
        if result.get("likely_suppressed"):
            st.error("Search Banまたは抑制疑いあり → 話題の欄表示リスク高")
        else:
            st.success("抑制兆候なし（アカウントレベル）")

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
            # API呼び出しで分析結果表示（省略）
