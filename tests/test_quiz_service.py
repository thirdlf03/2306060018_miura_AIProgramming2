"""
quiz_service.pyのテスト
"""

import pytest
import random
from datetime import datetime
from unittest.mock import patch, MagicMock
from models import Holiday
from services.quiz_service import (
    get_countries_for_quiz,
    get_holidays_for_country,
    generate_random_date,
    generate_true_false_question,
    generate_guess_question,
    check_true_false_answer,
    check_guess_answer,
    calculate_accuracy,
)


class TestQuizService:
    """quiz_service.pyの関数のテスト"""

    @patch("services.quiz_service.repository.get_available_countries")
    def test_get_countries_for_quiz_success(self, mock_repo_get, sample_countries):
        """クイズ用の国一覧取得成功テスト"""
        # モックの設定
        mock_repo_get.return_value = sample_countries

        result = get_countries_for_quiz()

        assert result == sample_countries
        mock_repo_get.assert_called_once()

    @patch("services.quiz_service.repository.get_available_countries")
    def test_get_countries_for_quiz_exception(self, mock_repo_get):
        """クイズ用の国一覧取得失敗テスト（例外発生）"""
        # モックの設定
        mock_repo_get.side_effect = Exception("Some error")

        # Streamlitのキャッシュをクリア
        get_countries_for_quiz.clear()

        with pytest.raises(Exception, match="Some error"):
            get_countries_for_quiz()

    @patch("services.quiz_service.repository.get_public_holidays")
    def test_get_holidays_for_country_success(self, mock_repo_get, sample_holidays):
        """指定された国の祝日一覧取得成功テスト"""
        # モックの設定
        mock_repo_get.return_value = sample_holidays

        result = get_holidays_for_country(2025, "JP")

        assert result == sample_holidays
        mock_repo_get.assert_called_once_with(2025, "JP")

    @patch("services.quiz_service.repository.get_public_holidays")
    def test_get_holidays_for_country_exception(self, mock_repo_get):
        """指定された国の祝日一覧取得失敗テスト（例外発生）"""
        # モックの設定
        mock_repo_get.side_effect = Exception("Some error")

        # Streamlitのキャッシュをクリア
        get_holidays_for_country.clear()

        with pytest.raises(Exception, match="Some error"):
            get_holidays_for_country(2025, "JP")

    def test_generate_random_date(self):
        """ランダムな日付生成テスト"""
        year = 2025
        result = generate_random_date(year)

        assert isinstance(result, datetime)
        assert result.year == year
        assert result.month >= 1
        assert result.month <= 12
        assert result.day >= 1
        assert result.day <= 31

    def test_generate_random_date_different_years(self):
        """異なる年でのランダムな日付生成テスト"""
        year1 = 2023
        year2 = 2024

        result1 = generate_random_date(year1)
        result2 = generate_random_date(year2)

        assert result1.year == year1
        assert result2.year == year2

    @patch("services.quiz_service.repository.get_available_countries")
    @patch("services.quiz_service.repository.get_public_holidays")
    def test_generate_true_false_question_holiday_true(
        self, mock_repo_get_holidays, mock_repo_get_countries, sample_countries
    ):
        """真偽問題生成テスト（祝日が正解の場合）"""
        # モックの設定
        mock_repo_get_countries.return_value = sample_countries

        holidays = [
            Holiday(
                date="2025-01-01",
                name="New Year's Day",
                local_name="元日",
                country_code="JP",
            )
        ]
        mock_repo_get_holidays.return_value = holidays

        # random.choiceとrandom.randintをモック化
        with (
            patch("random.choice") as mock_random_choice,
            patch("random.randint") as mock_random_randint,
        ):
            # generate_true_false_question内では、random.choiceが3回呼ばれる:
            # 1. 国の選択
            # 2. 祝日/非祝日の選択
            # 3. 祝日の選択（is_holidayがTrueの場合）
            mock_random_choice.side_effect = [sample_countries[0], True, holidays[0]]
            mock_random_randint.return_value = 2023

            result = generate_true_false_question()

            assert result is not None
            assert result["is_holiday"] is True
            assert result["country_code"] == "JP"
            assert result["date"] == "2025-01-01"
            assert result["holiday_name"] == "New Year's Day"

    @patch("services.quiz_service.repository.get_available_countries")
    @patch("services.quiz_service.repository.get_public_holidays")
    def test_generate_true_false_question_holiday_false(
        self, mock_repo_get_holidays, mock_repo_get_countries, sample_countries
    ):
        """真偽問題生成テスト（非祝日が正解の場合）"""
        # モックの設定
        mock_repo_get_countries.return_value = sample_countries
        mock_repo_get_holidays.return_value = []

        # random.choiceとrandom.randintをモック化
        with (
            patch("random.choice") as mock_random_choice,
            patch("random.randint") as mock_random_randint,
        ):
            mock_random_choice.side_effect = [sample_countries[0], False]
            mock_random_randint.return_value = 2023

            result = generate_true_false_question()

            assert result is not None
            assert result["is_holiday"] is False
            assert result["country_code"] == "JP"
            assert result["holiday_name"] is None

    @patch("services.quiz_service.repository.get_available_countries")
    def test_generate_true_false_question_no_countries(self, mock_repo_get):
        """真偽問題生成テスト（国一覧が取得できない場合）"""
        # モックの設定
        mock_repo_get.side_effect = Exception("Some error")

        # Streamlitのキャッシュをクリア
        get_countries_for_quiz.clear()

        with pytest.raises(Exception, match="Some error"):
            generate_true_false_question()

    @patch("services.quiz_service.repository.get_available_countries")
    def test_generate_guess_question_insufficient_countries(self, mock_repo_get):
        """推測問題生成テスト（国が不足している場合）"""
        # モックの設定
        mock_repo_get.return_value = [
            {"countryCode": "JP", "name": "Japan"},
            {"countryCode": "US", "name": "United States"},
        ]  # 2国のみ

        result = generate_guess_question()

        assert result is None

    @patch("services.quiz_service.repository.get_available_countries")
    @patch("services.quiz_service.repository.get_public_holidays")
    def test_generate_guess_question_no_holidays(
        self, mock_repo_get_holidays, mock_repo_get_countries, sample_countries
    ):
        """推測問題生成テスト（祝日が取得できない場合）"""
        # モックの設定
        mock_repo_get_countries.return_value = sample_countries
        mock_repo_get_holidays.return_value = []

        # random.sample、random.choice、random.randint、random.shuffleをモック化
        with (
            patch("random.sample") as mock_random_sample,
            patch("random.choice") as mock_random_choice,
            patch("random.randint") as mock_random_randint,
            patch("random.shuffle") as mock_random_shuffle,
        ):
            mock_random_sample.return_value = sample_countries[:4]
            mock_random_choice.side_effect = [sample_countries[0]]
            mock_random_randint.side_effect = [2023, 1, 1]  # year, month, day
            mock_random_shuffle.return_value = None

            result = generate_guess_question()

            assert result is None

    def test_check_true_false_answer_correct(self):
        """真偽問題の正解チェックテスト"""
        question = {"is_holiday": True}

        result = check_true_false_answer(question, True)

        assert result is True

    def test_check_true_false_answer_incorrect(self):
        """真偽問題の不正解チェックテスト"""
        question = {"is_holiday": False}

        result = check_true_false_answer(question, True)

        assert result is False

    def test_check_guess_answer_correct(self):
        """推測問題の正解チェックテスト"""
        question = {"correct_index": 2}

        result = check_guess_answer(question, 2)

        assert result is True

    def test_check_guess_answer_incorrect(self):
        """推測問題の不正解チェックテスト"""
        question = {"correct_index": 2}

        result = check_guess_answer(question, 1)

        assert result is False

    def test_calculate_accuracy_perfect_score(self):
        """正答率計算テスト（満点）"""
        result = calculate_accuracy(5, 5)

        assert result == 100.0

    def test_calculate_accuracy_half_score(self):
        """正答率計算テスト（半分）"""
        result = calculate_accuracy(3, 6)

        assert result == 50.0

    def test_calculate_accuracy_zero_score(self):
        """正答率計算テスト（0点）"""
        result = calculate_accuracy(0, 5)

        assert result == 0.0

    def test_calculate_accuracy_zero_total(self):
        """正答率計算テスト（問題数0）"""
        result = calculate_accuracy(0, 0)

        assert result == 0.0

    def test_calculate_accuracy_decimal_result(self):
        """正答率計算テスト（小数点あり）"""
        result = calculate_accuracy(7, 9)

        # 7/9 * 100 = 77.777...%
        assert abs(result - 77.78) < 0.01
