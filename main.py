import streamlit as st
import repository
from datetime import datetime
from constants import APP_TITLE, PAGE_ICON_MAIN, API_CACHE_TTL


# ページの基本設定
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON_MAIN,
    layout="wide",
    initial_sidebar_state="expanded",
)

# session_stateの初期化
if "favorites" not in st.session_state:
    try:
        st.session_state.favorites = repository.load_favorites()
    except Exception as e:
        st.error(f"お気に入りの読み込みに失敗しました: {str(e)}")
        st.session_state.favorites = []

# アプリのタイトルと説明
st.title(f"{PAGE_ICON_MAIN} {APP_TITLE}")
st.markdown("### World Holidays Explorer")

st.markdown("""
このアプリでは、世界中の祝日を探索して、みんなで共有できます！

**主な機能:**
- 🔍 **祝日検索**: 国と年を指定して祝日を検索
- ❤️ **みんなのお気に入り**: コミュニティで共有する祝日リスト
- 🎯 **クイズ**: 祝日に関する知識をテスト
""")

# 使い方ガイド
with st.expander("📖 使い方ガイド"):
    st.markdown("""
    ### 使い方
    
    1. **祝日を検索する**
       - 左側のメニューから「🔍 祝日検索」を選択
       - 国と年を選んで検索ボタンをクリック
       - 気になる祝日をみんなのお気に入りに追加
    
    2. **みんなのお気に入りを確認する**
       - 左側のメニューから「❤️ みんなのお気に入り」を選択
       - コミュニティが選んだ祝日を確認
       - 国別ランキングや統計情報を閲覧
    
    3. **クイズで学習する**
       - 左側のメニューから「⭕❌ マルバツクイズ」または「🎯 祝日名当てクイズ」を選択
       - 楽しみながら世界の祝日について学習
    
    **コミュニティ機能について:**
    - お気に入りは全ユーザーで共有されます
    - みんなが選んだ祝日から世界のトレンドを知ることができます
    """)

# 今日の日付と国別の祝日情報（オプション）
col1, col2 = st.columns(2)

with col1:
    st.info(f"📅 今日の日付: {datetime.now().strftime('%Y年%m月%d日')}")

with col2:
    # 利用可能な国数を表示
    try:
        countries = st.cache_data(ttl=API_CACHE_TTL)(
            repository.get_available_countries
        )()
        if countries:
            st.success(f"🌍 {len(countries)}ヶ国の祝日データが利用可能")
    except Exception as e:
        st.error(f"国リストの取得に失敗しました: {str(e)}")

# サイドバーの案内
st.sidebar.markdown("### 📱 ナビゲーション")
st.sidebar.info("左側のメニューから機能を選択してください")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 コミュニティ機能")
st.sidebar.caption("・お気に入りは全ユーザーで共有")
st.sidebar.caption("・みんなで世界の祝日を探索")

# ページへのナビゲーションボタン
st.markdown("### 🚀 クイックアクセス")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 祝日検索", use_container_width=True):
        st.switch_page("pages/1_Search.py")

with col2:
    if st.button("⭕❌ マルバツクイズ", use_container_width=True):
        st.switch_page("pages/2_True_False_Quiz.py")

with col3:
    if st.button("🎯 祝日名当てクイズ", use_container_width=True):
        st.switch_page("pages/3_Guess_Quiz.py")

with col4:
    if st.button("❤️ みんなのお気に入り", use_container_width=True):
        st.switch_page("pages/4_Favorites.py")

# フッター
st.markdown("---")
st.markdown("祝日データは[Nager.Date API](https://date.nager.at/)から取得しています")
