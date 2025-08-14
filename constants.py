"""
定数定義ファイル
アプリケーション全体で使用される定数を一元管理
"""

# API関連
API_BASE_URL = "https://date.nager.at/api/v3"
API_CACHE_TTL = 3600  # 1時間

# ファイルパス
FAVORITES_CSV_PATH = "data/favorites.csv"

# 年の範囲
YEAR_MIN = 1900
YEAR_MAX = 2100

# 日数
NEXT_HOLIDAYS_DAYS = 365

# 月名（日本語）
MONTH_NAMES = [
    "",  # 0は使わない
    "1月",
    "2月",
    "3月",
    "4月",
    "5月",
    "6月",
    "7月",
    "8月",
    "9月",
    "10月",
    "11月",
    "12月",
]

# ページタイトル
APP_TITLE = "世界の祝日アプリ"
PAGE_TITLE_SEARCH = "祝日検索"
PAGE_TITLE_TRUE_FALSE_QUIZ = "マルバツクイズ"
PAGE_TITLE_GUESS_QUIZ = "祝日名当てクイズ"
PAGE_TITLE_FAVORITES = "みんなのお気に入り"

# ページアイコン
PAGE_ICON_MAIN = "🌍"
PAGE_ICON_SEARCH = "🔍"
PAGE_ICON_TRUE_FALSE = "⭕"
PAGE_ICON_GUESS = "🎯"
PAGE_ICON_FAVORITES = "❤️"
