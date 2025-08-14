import streamlit as st
from datetime import datetime
from services import favorite_service, holiday_service
from constants import (
    APP_TITLE,
    PAGE_TITLE_SEARCH,
    PAGE_ICON_SEARCH,
    MONTH_NAMES,
    YEAR_MIN,
    YEAR_MAX,
)


st.set_page_config(
    page_title=f"{PAGE_TITLE_SEARCH} - {APP_TITLE}",
    page_icon=PAGE_ICON_SEARCH,
    layout="wide",
)

st.title(f"{PAGE_ICON_SEARCH} {PAGE_TITLE_SEARCH}")
st.markdown(
    "国と年を指定して、世界中の祝日を探索し、みんなのお気に入りに追加しましょう！"
)

# セッション状態の初期化
if "favorites" not in st.session_state:
    try:
        st.session_state.favorites = favorite_service.load_favorites()
    except Exception as e:
        st.error(str(e))
        st.session_state.favorites = []

# 検索結果をセッション状態に保存
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "search_country_code" not in st.session_state:
    st.session_state.search_country_code = None
if "search_year" not in st.session_state:
    st.session_state.search_year = None
if "search_country_display" not in st.session_state:
    st.session_state.search_country_display = None

# 検索フォーム
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # 国の選択
    country_options = holiday_service.get_country_options()

    if country_options:
        selected_country_display = st.selectbox(
            "国を選択", options=list(country_options.keys()), index=0
        )
        selected_country_code = country_options[selected_country_display]
    else:
        st.error("国リストの取得に失敗しました。")
        selected_country_code = None

with col2:
    # 年の選択
    current_year = datetime.now().year
    selected_year = st.number_input(
        "年を選択", min_value=YEAR_MIN, max_value=YEAR_MAX, value=current_year, step=1
    )

with col3:
    # 検索ボタン
    st.markdown("<br>", unsafe_allow_html=True)  # スペーサー
    search_button = st.button("🔍 検索", use_container_width=True, type="primary")

# 検索実行時の処理
if search_button and selected_country_code:
    with st.spinner("祝日データを取得中..."):
        try:
            holidays = holiday_service.get_public_holidays(
                selected_year, selected_country_code
            )
            # 検索結果をセッション状態に保存
            st.session_state.search_results = holidays
            st.session_state.search_country_code = selected_country_code
            st.session_state.search_year = selected_year
            st.session_state.search_country_display = selected_country_display
        except Exception as e:
            st.error(f"祝日データの取得に失敗しました: {str(e)}")
            st.session_state.search_results = []

# 検索結果の表示（セッション状態から取得）
holidays = st.session_state.search_results
selected_country_code = st.session_state.search_country_code
selected_year = st.session_state.search_year
selected_country_display = st.session_state.search_country_display

if holidays:
    st.success(f"{len(holidays)}件の祝日が見つかりました！")

    # データフレームに変換
    df = holiday_service.holidays_to_search_dataframe(
        holidays, st.session_state.favorites
    )

    # データエディタで表示（お気に入り列を編集可能に）
    edited_df = st.data_editor(
        df,
        column_config={
            "お気に入り": st.column_config.CheckboxColumn(
                "お気に入り",
                help="チェックを入れてみんなのお気に入りに追加",
                default=False,
            )
        },
        disabled=["日付", "祝日名", "現地名", "国コード"],
        hide_index=True,
        use_container_width=True,
        key="holiday_editor",
    )

    # お気に入りの変更を自動検知して更新
    if not df.equals(edited_df):
        try:
            # お気に入りリストを更新
            new_favorites = favorite_service.update_favorites_from_search(
                st.session_state.favorites,
                edited_df,
                holidays,
                selected_country_code,
            )

            # セッション状態とCSVファイルを更新
            st.session_state.favorites = new_favorites
            favorite_service.save_favorites(new_favorites)

            # 成功メッセージを表示（一時的に）
            success_placeholder = st.empty()
            success_placeholder.success("✅ みんなのお気に入りを更新しました！")

            # 検索結果を再表示するためにページを再実行
            st.rerun()
        except Exception as e:
            st.error(f"お気に入りの更新に失敗しました: {str(e)}")

    # 統計情報
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("祝日数", len(holidays))

    with col2:
        favorite_count = len(
            [row for _, row in edited_df.iterrows() if row["お気に入り"]]
        )
        st.metric("みんなのお気に入り登録数", favorite_count)

    with col3:
        # 月別の分布
        stats = favorite_service.get_favorites_statistics(holidays)
        if stats and "most_month" in stats:
            st.metric("最も祝日が多い月", MONTH_NAMES[stats["most_month"]])

elif (
    st.session_state.search_results is not None
    and len(st.session_state.search_results) == 0
):
    st.warning(
        f"{selected_year}年の{selected_country_display}の祝日データが見つかりませんでした。"
    )

# 使い方のヒント
with st.expander("💡 使い方のヒント"):
    st.markdown("""
    - 国を選択して年を指定し、検索ボタンをクリックすると祝日一覧が表示されます
    - お気に入り列のチェックボックスをクリックすると、**みんなのお気に入り**に追加されます
    - お気に入りは全ユーザーで共有されます
    - みんなで楽しむため、マナーを守って利用しましょう
    """)

# 現在のお気に入り数を表示
st.sidebar.markdown("---")
st.sidebar.info(f"みんなのお気に入り: {len(st.session_state.favorites)}件")
st.sidebar.caption("※ 全ユーザー共通のお気に入りリストです")
