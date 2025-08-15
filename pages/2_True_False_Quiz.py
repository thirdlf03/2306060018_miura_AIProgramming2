import streamlit as st
from services.quiz_service import (
    generate_true_false_question,
    check_true_false_answer,
    calculate_accuracy,
)
from constants import APP_TITLE, PAGE_TITLE_TRUE_FALSE_QUIZ, PAGE_ICON_TRUE_FALSE


st.set_page_config(
    page_title=f"{PAGE_TITLE_TRUE_FALSE_QUIZ} - {APP_TITLE}",
    page_icon=PAGE_ICON_TRUE_FALSE,
    layout="wide",
)

st.title(f"{PAGE_ICON_TRUE_FALSE}❌ {PAGE_TITLE_TRUE_FALSE_QUIZ}")
st.markdown("指定された日付が本当に祝日かどうかを当ててみましょう！")

# セッション状態の初期化
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_total" not in st.session_state:
    st.session_state.quiz_total = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = False


# 新しい問題を生成
if st.session_state.current_question is None:
    st.session_state.current_question = generate_true_false_question()
    st.session_state.quiz_answered = False

# スコア表示
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("正解数", st.session_state.quiz_score)
with col2:
    st.metric("問題数", st.session_state.quiz_total)
with col3:
    accuracy = calculate_accuracy(
        st.session_state.quiz_score, st.session_state.quiz_total
    )
    st.metric("正答率", f"{accuracy:.1f}%")

st.markdown("---")

# 問題表示
if st.session_state.current_question:
    question = st.session_state.current_question

    # 問題文
    st.markdown("### 問題")
    st.info(f"""
    **{question["country_name"]}** 🏳️ の **{question["date"]}** は祝日でしょうか？
    """)

    # 回答前の状態
    if not st.session_state.quiz_answered:
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("⭕ 祝日である", use_container_width=True, type="primary"):
                is_correct = check_true_false_answer(
                    st.session_state.current_question, True
                )
                st.session_state.quiz_total += 1
                if is_correct:
                    st.session_state.quiz_score += 1
                st.session_state.quiz_answered = True
                st.rerun()

        with col2:
            if st.button("❌ 祝日ではない", use_container_width=True, type="secondary"):
                is_correct = check_true_false_answer(
                    st.session_state.current_question, False
                )
                st.session_state.quiz_total += 1
                if is_correct:
                    st.session_state.quiz_score += 1
                st.session_state.quiz_answered = True
                st.rerun()

    # 回答後の状態
    else:
        # 結果表示
        if st.session_state.current_question["is_holiday"]:
            if st.session_state.quiz_answered:
                correct_answer = "⭕ 祝日である"
                st.success(f"正解は: {correct_answer}")
                st.markdown(f"""
                **祝日名**: {question["holiday_name"]}  
                **現地名**: {question["local_name"]}
                """)
        else:
            if st.session_state.quiz_answered:
                correct_answer = "❌ 祝日ではない"
                st.error(f"正解は: {correct_answer}")
                st.markdown("この日は祝日ではありません。")

        # 次の問題へ
        if st.button("🔄 次の問題", use_container_width=True, type="primary"):
            st.session_state.current_question = generate_true_false_question()
            st.session_state.quiz_answered = False
            st.rerun()
else:
    st.error("問題の生成に失敗しました。インターネット接続を確認してください。")

# リセットボタン
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("🔄 スコアをリセット", use_container_width=True):
        st.session_state.quiz_score = 0
        st.session_state.quiz_total = 0
        st.session_state.current_question = generate_true_false_question()
        st.session_state.quiz_answered = False
        st.rerun()

# 使い方
with st.expander("💡 遊び方"):
    st.markdown("""
    1. 表示された国と日付の組み合わせが祝日かどうかを考えます
    2. 「⭕ 祝日である」または「❌ 祝日ではない」をクリックして回答
    3. 正解が表示されたら「次の問題」をクリック
    4. スコアは自動的に記録されます
    
    **ヒント**: 
    - 祝日は国によって大きく異なります
    - 同じ日でも国が違えば祝日かどうかは変わります
    - クリスマスや新年は多くの国で祝日ですが、すべてではありません
    """)

# サイドバーに統計情報
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 クイズ統計")
if st.session_state.quiz_total > 0:
    st.sidebar.progress(st.session_state.quiz_score / st.session_state.quiz_total)
    st.sidebar.markdown(
        f"正解数: {st.session_state.quiz_score} / {st.session_state.quiz_total}"
    )
