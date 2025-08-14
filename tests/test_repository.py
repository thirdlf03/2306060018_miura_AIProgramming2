"""
repository.pyのテスト
"""

import pytest
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from models import Holiday
from repository import (
    get_available_countries,
    get_public_holidays,
    load_favorites,
    save_favorites,
    get_next_public_holidays,
)


class TestRepository:
    """repository.pyの関数のテスト"""

    @patch("repository.requests.get")
    def test_get_available_countries_success(self, mock_get, sample_countries):
        """利用可能な国の取得成功テスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.json.return_value = sample_countries
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_available_countries()

        assert result == sample_countries
        mock_get.assert_called_once_with(
            "https://date.nager.at/api/v3/AvailableCountries"
        )

    @patch("repository.requests.get")
    def test_get_available_countries_api_error(self, mock_get):
        """利用可能な国の取得失敗テスト（APIエラー）"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="API Error"):
            get_available_countries()

    @patch("repository.requests.get")
    def test_get_public_holidays_success(
        self, mock_get, sample_api_response, sample_holidays
    ):
        """指定された年と国の祝日一覧取得成功テスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_public_holidays(2025, "JP")

        assert len(result) == 2
        assert result[0].date == "2025-01-01"
        assert result[0].name == "New Year's Day"
        assert result[0].country_code == "JP"
        mock_get.assert_called_once_with(
            "https://date.nager.at/api/v3/PublicHolidays/2025/JP"
        )

    @patch("repository.requests.get")
    def test_get_public_holidays_api_error(self, mock_get):
        """指定された年と国の祝日一覧取得失敗テスト（APIエラー）"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="API Error"):
            get_public_holidays(2025, "JP")

    @patch("repository.requests.get")
    def test_get_next_public_holidays_success(self, mock_get, sample_api_response):
        """今後の祝日取得成功テスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_next_public_holidays("JP")

        assert len(result) == 2
        mock_get.assert_called_once_with(
            "https://date.nager.at/api/v3/NextPublicHolidays/JP"
        )

    @patch("repository.requests.get")
    def test_get_next_public_holidays_api_error(self, mock_get):
        """今後の祝日取得失敗テスト（APIエラー）"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="API Error"):
            get_next_public_holidays("JP")

    @patch("repository.pd.read_csv")
    @patch("repository.Path")
    def test_load_favorites_existing_file(
        self, mock_path, mock_read_csv, sample_holidays
    ):
        """既存のCSVファイルからのお気に入り読み込みテスト"""
        # モックの設定
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        # CSVデータのモック
        csv_data = [
            {
                "date": "2025-01-01",
                "name": "New Year's Day",
                "local_name": "元日",
                "country_code": "JP",
            },
            {
                "date": "2025-01-13",
                "name": "Coming of Age Day",
                "local_name": "成人の日",
                "country_code": "JP",
            },
        ]
        mock_df = pd.DataFrame(csv_data)
        mock_read_csv.return_value = mock_df

        result = load_favorites()

        assert len(result) == 2
        assert result[0].date == "2025-01-01"
        assert result[0].name == "New Year's Day"
        assert result[0].country_code == "JP"

    @patch("repository.Path")
    def test_load_favorites_file_not_exists(self, mock_path):
        """CSVファイルが存在しない場合のお気に入り読み込みテスト"""
        # モックの設定
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        result = load_favorites()

        assert result == []

    @patch("repository.pd.read_csv")
    @patch("repository.Path")
    def test_load_favorites_empty_file(self, mock_path, mock_read_csv):
        """空のCSVファイルからのお気に入り読み込みテスト"""
        # モックの設定
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_df = pd.DataFrame()
        mock_read_csv.return_value = mock_df

        result = load_favorites()

        assert result == []

    @patch("repository.pd.DataFrame")
    @patch("repository.Path")
    def test_save_favorites_success(self, mock_path, mock_dataframe, sample_holidays):
        """お気に入りの保存成功テスト"""
        # モックの設定
        mock_path_instance = MagicMock()
        mock_path_instance.parent.mkdir.return_value = None
        mock_path.return_value = mock_path_instance

        mock_df_instance = MagicMock()
        mock_dataframe.return_value = mock_df_instance

        save_favorites(sample_holidays)

        # ディレクトリ作成が呼ばれることを確認
        mock_path_instance.parent.mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )
        # DataFrameの作成と保存が呼ばれることを確認
        mock_dataframe.assert_called_once()
        mock_df_instance.to_csv.assert_called_once_with(mock_path_instance, index=False)

    @patch("repository.pd.DataFrame")
    @patch("repository.Path")
    def test_save_favorites_empty_list(self, mock_path, mock_dataframe):
        """空のお気に入りリストの保存テスト"""
        # モックの設定
        mock_path_instance = MagicMock()
        mock_path_instance.parent.mkdir.return_value = None
        mock_path.return_value = mock_path_instance

        mock_df_instance = MagicMock()
        mock_dataframe.return_value = mock_df_instance

        save_favorites([])

        # 空のリストでも保存処理が実行されることを確認
        mock_dataframe.assert_called_once_with([])
        mock_df_instance.to_csv.assert_called_once_with(mock_path_instance, index=False)
