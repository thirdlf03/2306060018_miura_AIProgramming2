"""
holiday_service.pyのテスト
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from models import Holiday
from services.holiday_service import (
    get_available_countries,
    get_public_holidays,
    get_next_public_holidays,
    get_country_options,
    holidays_to_search_dataframe,
)


class TestHolidayService:
    """holiday_service.pyの関数のテスト"""

    @patch("services.holiday_service.repository.get_available_countries")
    def test_get_available_countries_success(self, mock_repo_get, sample_countries):
        """利用可能な国の取得成功テスト"""
        # モックの設定
        mock_repo_get.return_value = sample_countries

        result = get_available_countries()

        assert result == sample_countries
        mock_repo_get.assert_called_once()

    @patch("services.holiday_service.repository.get_available_countries")
    def test_get_available_countries_repository_error(self, mock_repo_get):
        """利用可能な国の取得失敗テスト（リポジトリエラー）"""
        # モックの設定
        mock_repo_get.side_effect = Exception("Repository Error")

        # Streamlitのキャッシュをクリア
        get_available_countries.clear()

        with pytest.raises(Exception, match="Repository Error"):
            get_available_countries()

    @patch("services.holiday_service.repository.get_public_holidays")
    def test_get_public_holidays_success(self, mock_repo_get, sample_holidays):
        """指定された年と国の祝日一覧取得成功テスト"""
        # モックの設定
        mock_repo_get.return_value = sample_holidays

        result = get_public_holidays(2025, "JP")

        assert result == sample_holidays
        mock_repo_get.assert_called_once_with(2025, "JP")

    @patch("services.holiday_service.repository.get_next_public_holidays")
    def test_get_next_public_holidays_success(self, mock_repo_get, sample_holidays):
        """今後の祝日取得成功テスト"""
        # モックの設定
        mock_repo_get.return_value = sample_holidays

        result = get_next_public_holidays("JP")

        assert result == sample_holidays
        mock_repo_get.assert_called_once_with("JP")

    @patch("services.holiday_service.get_available_countries")
    def test_get_country_options_success(self, mock_get_countries, sample_countries):
        """国選択用オプション辞書生成成功テスト"""
        # モックの設定
        mock_get_countries.return_value = sample_countries

        result = get_country_options()

        expected = {
            "Japan (JP)": "JP",
            "United States (US)": "US",
            "Germany (DE)": "DE",
        }
        assert result == expected

    @patch("services.holiday_service.get_available_countries")
    def test_get_country_options_empty_list(self, mock_get_countries):
        """空の国リストでのオプション辞書生成テスト"""
        # モックの設定
        mock_get_countries.return_value = []

        result = get_country_options()

        assert result == {}

    @patch("services.holiday_service.get_available_countries")
    def test_get_country_options_exception(self, mock_get_countries):
        """例外発生時のオプション辞書生成テスト"""
        # モックの設定
        mock_get_countries.side_effect = Exception("Some error")

        result = get_country_options()

        assert result == {}

    def test_holidays_to_search_dataframe_with_favorites(self, sample_holidays):
        """お気に入り状態付きの検索結果DataFrame生成テスト"""
        # お気に入りリストを作成（最初の祝日のみ）
        favorites = [sample_holidays[0]]

        result = holidays_to_search_dataframe(sample_holidays, favorites)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

        # 列の確認
        expected_columns = ["日付", "祝日名", "現地名", "国コード", "お気に入り"]
        assert list(result.columns) == expected_columns

        # お気に入り状態の確認
        assert result.iloc[0]["お気に入り"] == True  # 最初の祝日
        assert result.iloc[1]["お気に入り"] == False  # 2番目の祝日
        assert result.iloc[2]["お気に入り"] == False  # 3番目の祝日

    def test_holidays_to_search_dataframe_empty_holidays(self):
        """空の祝日リストでのDataFrame生成テスト"""
        result = holidays_to_search_dataframe([], [])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == [
            "日付",
            "祝日名",
            "現地名",
            "国コード",
            "お気に入り",
        ]

    def test_holidays_to_search_dataframe_empty_favorites(self, sample_holidays):
        """空のお気に入りリストでのDataFrame生成テスト"""
        result = holidays_to_search_dataframe(sample_holidays, [])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

        # すべてのお気に入り状態がFalseであることを確認
        assert all(result["お気に入り"] == False)

    def test_holidays_to_search_dataframe_data_integrity(self, sample_holidays):
        """DataFrameのデータ整合性テスト"""
        favorites = []
        result = holidays_to_search_dataframe(sample_holidays, favorites)

        # データの整合性を確認
        assert result.iloc[0]["日付"] == "2025-01-01"
        assert result.iloc[0]["祝日名"] == "New Year's Day"
        assert result.iloc[0]["現地名"] == "元日"
        assert result.iloc[0]["国コード"] == "JP"

        assert result.iloc[1]["日付"] == "2025-01-13"
        assert result.iloc[1]["祝日名"] == "Coming of Age Day"
        assert result.iloc[1]["現地名"] == "成人の日"
        assert result.iloc[1]["国コード"] == "JP"
