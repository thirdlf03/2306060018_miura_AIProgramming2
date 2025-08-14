import streamlit as st
import pandas as pd
from constants import (
    APP_TITLE,
    PAGE_TITLE_FAVORITES,
    PAGE_ICON_FAVORITES,
    MONTH_NAMES,
)
from services import favorite_service


st.set_page_config(
    page_title=f"{PAGE_TITLE_FAVORITES} - {APP_TITLE}",
    page_icon=PAGE_ICON_FAVORITES,
    layout="wide",
)

st.title(f"{PAGE_ICON_FAVORITES} {PAGE_TITLE_FAVORITES}")
st.markdown("みんながお気に入りに登録した世界の祝日を見てみましょう！")

# セッション状態の初期化
if "favorites" not in st.session_state:
    try:
        st.session_state.favorites = favorite_service.load_favorites()
    except Exception as e:
        st.error(str(e))
        st.session_state.favorites = []

# お気に入りデータの取得
favorites = st.session_state.favorites

if not favorites:
    st.info("まだ誰もお気に入りを登録していません。最初の投稿者になりましょう！")
else:
    # 統計情報の表示
    stats = favorite_service.get_favorites_statistics(favorites)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("みんなのお気に入り総数", f"{stats['total_holidays']}件")
    with col2:
        st.metric("登録されている国数", f"{stats['total_countries']}ヶ国")
    with col3:
        if "most_month" in stats:
            st.metric("人気の月", MONTH_NAMES[stats["most_month"]])

    # タブで表示を切り替え
    tab1, tab2, tab3 = st.tabs(
        ["📋 みんなのお気に入り一覧", "🌍 国別人気ランキング", "📊 コミュニティ統計"]
    )

    with tab1:
        st.subheader("みんなが選んだ祝日一覧")

        # データフレームの作成（削除列を含まない）
        df = favorite_service.get_favorites_dataframe(favorites)

        # 削除列を除外して表示
        display_df = df.drop(columns=["削除"]) if "削除" in df.columns else df

        # データフレームを表示（読み取り専用）
        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True,
        )

    with tab2:
        st.subheader("国別の人気祝日")

        # 国別にグループ化
        grouped_holidays = favorite_service.get_country_grouped_holidays(favorites)

        for country, holidays_df in grouped_holidays.items():
            with st.expander(f"{country} ({len(holidays_df)}件)"):
                st.dataframe(
                    holidays_df,
                    hide_index=True,
                    use_container_width=True,
                )

    with tab3:
        st.subheader("コミュニティの傾向")

        # 国別の分布
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### みんなが注目している国")
            if "country_stats" in stats:
                st.bar_chart(stats["country_stats"])

        with col2:
            st.markdown("#### 人気の月")
            if "month_stats" in stats:
                # 月名でラベル付け
                month_labels = [
                    MONTH_NAMES[month] for month in stats["month_stats"].index
                ]
                month_data = pd.Series(stats["month_stats"].values, index=month_labels)
                st.bar_chart(month_data)

        # 年別の分布
        st.markdown("#### 年別の登録傾向")
        if "year_stats" in stats:
            st.bar_chart(stats["year_stats"])

        # コミュニティインサイト
        st.markdown("---")
        st.markdown("### 🌟 コミュニティインサイト")

        insight_col1, insight_col2 = st.columns(2)

        with insight_col1:
            if "country_stats" in stats and len(stats["country_stats"]) > 0:
                top_country = stats["country_stats"].index[0]
                top_count = stats["country_stats"].iloc[0]
                st.info(f"**最も人気の国**: {top_country} ({top_count}件)")

        with insight_col2:
            if "most_month" in stats:
                popular_month = MONTH_NAMES[stats["most_month"]]
                month_count = stats["month_stats"][stats["most_month"]]
                st.info(f"**最も人気の月**: {popular_month} ({month_count}件)")

        # 参加を促すメッセージ
        st.markdown("---")
        st.success("🎉 みんなで世界の祝日を発見し、共有しましょう！")

# 使い方のヒント
with st.expander("💡 コミュニティ機能について"):
    st.markdown("""
    - これはみんなで共有するお気に入りリストです
    - 祝日検索ページでお気に入りに追加すると、全ユーザーに共有されます
    - 他のユーザーが追加した祝日も表示されます
    - 国別ランキングで人気の国を確認できます
    - 統計情報でコミュニティ全体の興味・関心を知ることができます
    - みんなで楽しむため、マナーを守って利用しましょう
    """)

# フッター
st.markdown("---")
st.caption(
    "💡 ヒント: 祝日検索ページから新しい祝日をみんなのお気に入りに追加できます！"
)
