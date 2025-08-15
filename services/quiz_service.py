import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import streamlit as st
import repository
from models import Holiday
from constants import API_CACHE_TTL


@st.cache_data(ttl=API_CACHE_TTL)
def get_countries_for_quiz() -> Optional[List[dict]]:
    """
    クイズ用の国一覧を取得

    Returns:
        List[dict]: 国一覧の辞書リスト、またはNone

    Raises:
        Exception: 国一覧の取得に失敗した場合
    """
    try:
        return repository.get_available_countries()
    except Exception as e:
        raise e


@st.cache_data(ttl=API_CACHE_TTL)
def get_holidays_for_country(year: int, country_code: str) -> Optional[List[Holiday]]:
    """
    指定された国の祝日一覧を取得

    Args:
        year: 年
        country_code: 国コード

    Returns:
        List[Holiday]: 祝日一覧、またはNone

    Raises:
        Exception: 祝日一覧の取得に失敗した場合
    """
    try:
        return repository.get_public_holidays(year, country_code)
    except Exception as e:
        raise e


def generate_random_date(year: int) -> datetime:
    """
    指定された年のランダムな日付を生成

    Args:
        year: 年

    Returns:
        datetime: ランダムな日付
    """
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)


def generate_true_false_question() -> Optional[Dict]:
    """
    真偽問題を生成

    Returns:
        Dict: 問題の辞書データ、またはNone
    """
    countries = get_countries_for_quiz()
    if not countries:
        return None

    # ランダムな国を選択
    country = random.choice(countries)
    country_code = country["countryCode"]
    country_name = country["name"]

    # ランダムな年を選択（2020-2025）
    year = random.randint(2020, 2025)

    # 50%の確率で祝日、50%の確率で非祝日を生成
    is_holiday = random.choice([True, False])

    if is_holiday:
        # 祝日を取得
        holidays = get_holidays_for_country(year, country_code)

        if holidays:
            holiday = random.choice(holidays)
            return {
                "country_name": country_name,
                "country_code": country_code,
                "date": holiday.date,
                "is_holiday": True,
                "holiday_name": holiday.name,
                "local_name": holiday.local_name,
            }
        else:
            # 祝日がない場合は非祝日を生成
            is_holiday = False

    if not is_holiday:
        # ランダムな日付を生成
        random_date = generate_random_date(year)

        # その国の祝日リストを取得
        holidays = get_holidays_for_country(year, country_code) or []
        holiday_dates = [h.date for h in holidays]

        # 祝日と重複しないようにする
        while random_date.strftime("%Y-%m-%d") in holiday_dates:
            random_date = generate_random_date(year)

        return {
            "country_name": country_name,
            "country_code": country_code,
            "date": random_date.strftime("%Y-%m-%d"),
            "is_holiday": False,
            "holiday_name": None,
            "local_name": None,
        }

    return None


def generate_guess_question() -> Optional[Dict]:
    """
    推測問題を生成

    Returns:
        Dict: 問題の辞書データ、またはNone
    """
    countries = get_countries_for_quiz()
    if not countries or len(countries) < 4:
        return None

    # ランダムに4つの国を選択
    selected_countries = random.sample(countries, 4)

    # 正解の国を選択
    correct_country = random.choice(selected_countries)
    correct_country_code = correct_country["countryCode"]
    correct_country_name = correct_country["name"]

    # ランダムな年を選択（2023-2025）
    year = random.randint(2023, 2025)

    # 正解の国の祝日を取得
    holidays = get_holidays_for_country(year, correct_country_code)
    if not holidays:
        return None

    # ランダムな祝日を選択
    correct_holiday = random.choice(holidays)

    # 選択肢を作成
    options = []

    # 正解
    options.append(
        {
            "date": correct_holiday.date,
            "country_code": correct_country_code,
            "country_name": correct_country_name,
            "is_correct": True,
        }
    )

    # 他の国の選択肢を3つ作成
    for country in selected_countries:
        if country["countryCode"] != correct_country_code:
            # その国の祝日を取得
            other_holidays = (
                get_holidays_for_country(year, country["countryCode"]) or []
            )

            if other_holidays:
                # ランダムな祝日を選択
                other_holiday = random.choice(other_holidays)
                options.append(
                    {
                        "date": other_holiday.date,
                        "country_code": country["countryCode"],
                        "country_name": country["name"],
                        "is_correct": False,
                    }
                )

    # 選択肢が4つ未満の場合はダミーの日付を生成
    while len(options) < 4:
        # ランダムな日付を生成
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # 月の最大は28日
        fake_date = f"{year}-{month:02d}-{day:02d}"

        # 既存の選択肢と重複しないようにする
        if not any(opt["date"] == fake_date for opt in options):
            fake_country = random.choice(selected_countries)
            options.append(
                {
                    "date": fake_date,
                    "country_code": fake_country["countryCode"],
                    "country_name": fake_country["name"],
                    "is_correct": False,
                }
            )

    # 選択肢をシャッフル
    random.shuffle(options)

    return {
        "holiday_name": correct_holiday.name,
        "local_name": correct_holiday.local_name,
        "options": options[:4],  # 4つの選択肢
        "correct_index": next(
            i for i, opt in enumerate(options[:4]) if opt["is_correct"]
        ),
    }


def check_true_false_answer(question: Dict, user_answer: bool) -> bool:
    """
    真偽問題の回答をチェック

    Args:
        question: 問題データ
        user_answer: ユーザーの回答

    Returns:
        bool: 正解かどうか
    """
    return user_answer == question["is_holiday"]


def check_guess_answer(question: Dict, selected_index: int) -> bool:
    """
    推測問題の回答をチェック

    Args:
        question: 問題データ
        selected_index: ユーザーが選択した選択肢のインデックス

    Returns:
        bool: 正解かどうか
    """
    return selected_index == question["correct_index"]


def calculate_accuracy(score: int, total: int) -> float:
    """
    正答率を計算

    Args:
        score: 正解数
        total: 問題数

    Returns:
        float: 正答率（パーセント）
    """
    if total == 0:
        return 0.0
    return (score / total) * 100


def process_guess_answer(
    question: Dict, selected_index: int, current_score: int, current_total: int
) -> Dict:
    """
    推測問題の回答を処理し、スコアを更新

    Args:
        question: 問題データ
        selected_index: ユーザーが選択した選択肢のインデックス
        current_score: 現在の正解数
        current_total: 現在の問題数

    Returns:
        Dict: 更新されたスコア情報
            - is_correct: 正解かどうか
            - new_score: 新しい正解数
            - new_total: 新しい問題数
    """
    is_correct = check_guess_answer(question, selected_index)
    new_total = current_total + 1
    new_score = current_score + 1 if is_correct else current_score

    return {"is_correct": is_correct, "new_score": new_score, "new_total": new_total}
