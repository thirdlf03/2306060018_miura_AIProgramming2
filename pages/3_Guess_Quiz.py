import streamlit as st
from services.quiz_service import (
    generate_guess_question as service_generate_guess_question,
    check_guess_answer as service_check_guess_answer,
    calculate_accuracy,
)
from constants import APP_TITLE, PAGE_TITLE_GUESS_QUIZ, PAGE_ICON_GUESS


st.set_page_config(
    page_title=f"{PAGE_TITLE_GUESS_QUIZ} - {APP_TITLE}",
    page_icon=PAGE_ICON_GUESS,
    layout="wide",
)

st.title(f"{PAGE_ICON_GUESS} {PAGE_TITLE_GUESS_QUIZ}")
st.markdown("祝日の名前から、いつ・どこの祝日かを当ててみましょう！")

# セッション状態の初期化
if "guess_score" not in st.session_state:
    st.session_state.guess_score = 0
if "guess_total" not in st.session_state:
    st.session_state.guess_total = 0
if "current_guess_question" not in st.session_state:
    st.session_state.current_guess_question = None
if "guess_answered" not in st.session_state:
    st.session_state.guess_answered = False
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None


def handle_guess_answer(selected_index):
    """ユーザーの回答をチェック"""
    is_correct = service_check_guess_answer(
        st.session_state.current_guess_question, selected_index
    )

    st.session_state.guess_total += 1
    if is_correct:
        st.session_state.guess_score += 1

    st.session_state.guess_answered = True
    st.session_state.selected_answer = selected_index
    return is_correct


# 新しい問題を生成
if st.session_state.current_guess_question is None:
    st.session_state.current_guess_question = service_generate_guess_question()
    st.session_state.guess_answered = False
    st.session_state.selected_answer = None

# スコア表示
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("正解数", st.session_state.guess_score)
with col2:
    st.metric("問題数", st.session_state.guess_total)
with col3:
    accuracy = calculate_accuracy(
        st.session_state.guess_score, st.session_state.guess_total
    )
    st.metric("正答率", f"{accuracy:.1f}%")

st.markdown("---")

# 問題表示
if st.session_state.current_guess_question:
    question = st.session_state.current_guess_question

    # 問題文
    st.markdown("### 問題")
    st.info(f"""
    **「{question["holiday_name"]}」**  
    （現地名: {question["local_name"]}）
    
    この祝日はいつ、どこの国の祝日でしょうか？
    """)

    # 回答前の状態
    if not st.session_state.guess_answered:
        # ラジオボタンで選択肢を表示
        option_texts = []
        for i, option in enumerate(question["options"]):
            option_text = f"{option['date']} - {option['country_name']} 🏳️"
            option_texts.append(option_text)

        selected = st.radio(
            "選択してください:", option_texts, index=None, key="guess_radio"
        )

        if selected:
            selected_index = option_texts.index(selected)
            if st.button("🎯 回答する", use_container_width=True, type="primary"):
                handle_guess_answer(selected_index)
                st.rerun()

    # 回答後の状態
    else:
        # 結果表示
        correct_option = question["options"][question["correct_index"]]

        # 選択肢を結果付きで表示
        for i, option in enumerate(question["options"]):
            option_text = f"{option['date']} - {option['country_name']} 🏳️"

            if i == question["correct_index"]:
                st.success(f"✅ {option_text} （正解）")
            elif i == st.session_state.selected_answer:
                st.error(f"❌ {option_text} （あなたの回答）")
            else:
                st.markdown(f"  {option_text}")

        # 次の問題へ
        st.markdown("")
        if st.button("🔄 次の問題", use_container_width=True, type="primary"):
            st.session_state.current_guess_question = service_generate_guess_question()
            st.session_state.guess_answered = False
            st.session_state.selected_answer = None
            st.rerun()
else:
    st.error("問題の生成に失敗しました。インターネット接続を確認してください。")

# リセットボタン
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("🔄 スコアをリセット", use_container_width=True):
        st.session_state.guess_score = 0
        st.session_state.guess_total = 0
        st.session_state.current_guess_question = service_generate_guess_question()
        st.session_state.guess_answered = False
        st.session_state.selected_answer = None
        st.rerun()

# 使い方
with st.expander("💡 遊び方"):
    st.markdown("""
    1. 表示された祝日の名前を見て、いつ・どこの国の祝日かを考えます
    2. 4つの選択肢から正解だと思うものを選択
    3. 「回答する」ボタンをクリック
    4. 正解が表示されたら「次の問題」をクリック
    
    **ヒント**: 
    - 「Christmas Day」や「New Year's Day」など、同じ名前でも国によって日付が異なることがあります
    - 祝日の名前から、その国の文化や宗教を推測できることがあります
    - 現地名も参考にしてみましょう
    """)

# サイドバーに統計情報
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 クイズ統計")
if st.session_state.guess_total > 0:
    st.sidebar.progress(st.session_state.guess_score / st.session_state.guess_total)
    st.sidebar.markdown(
        f"正解数: {st.session_state.guess_score} / {st.session_state.guess_total}"
    )

# 豆知識
with st.expander("🌍 豆知識"):
    st.markdown("""
    **世界の祝日の特徴:**
    
    - **キリスト教圏**: クリスマス、イースターなどの宗教的な祝日が多い
    - **イスラム教圏**: ラマダン明けの祝日（イード）など
    - **アジア**: 旧正月、中秋節など旧暦に基づく祝日
    - **国民の祝日**: 独立記念日、革命記念日など各国固有の祝日
    
    同じ「New Year」でも、西暦の1月1日を祝う国もあれば、旧暦の正月を祝う国もあります！
    """)
