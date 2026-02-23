# utils/risky_words.py
import re

# 高リスクワードのパターン（正規表現）。大文字小文字無視でマッチ
RISKY_WORDS = [
    r'\bちんぽ\b', r'\bちんこ\b', r'\bちんちん\b',
    r'\bまんこ\b', r'\bおまんこ\b', r'\bまんまん\b',
    r'\bクリトリス\b', r'\bクリ\b',
    r'\bフェラ\b', r'\bフェラチオ\b',
    r'\bセックス\b', r'\bセク\b',
    r'\b挿入\b', r'\b中出し\b', r'\b外出し\b',
    r'\b射精\b', r'\b精液\b', r'\bザーメン\b',
    r'\bおっぱい\b', r'\bパイパン\b', r'\b巨乳\b',
    # 必要に応じて追加（例: 英語混じり、隠語など）
    r'\bpussy\b', r'\bcock\b', r'\bporn\b',
]
