"""
pytestの共通設定とフィクスチャ
"""
import pytest
import pandas as pd
from pathlib import Path
from models import Holiday


@pytest.fixture
def sample_holidays():
    """テスト用のサンプル祝日データ"""
    return [
        Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="JP"
        ),
        Holiday(
            date="2025-01-13",
            name="Coming of Age Day",
            local_name="成人の日",
            country_code="JP"
        ),
        Holiday(
            date="2025-02-11",
            name="National Foundation Day",
            local_name="建国記念の日",
            country_code="JP"
        )
    ]


@pytest.fixture
def sample_countries():
    """テスト用のサンプル国データ"""
    return [
        {
            "name": "Japan",
            "countryCode": "JP"
        },
        {
            "name": "United States",
            "countryCode": "US"
        },
        {
            "name": "Germany",
            "countryCode": "DE"
        }
    ]


@pytest.fixture
def sample_api_response():
    """テスト用のサンプルAPIレスポンス"""
    return [
        {
            "date": "2025-01-01",
            "name": "New Year's Day",
            "localName": "元日",
            "countryCode": "JP"
        },
        {
            "date": "2025-01-13",
            "name": "Coming of Age Day",
            "localName": "成人の日",
            "countryCode": "JP"
        }
    ]


@pytest.fixture
def temp_csv_path(tmp_path):
    """テスト用の一時的なCSVファイルパス"""
    return tmp_path / "test_favorites.csv"


@pytest.fixture
def sample_favorites_dataframe():
    """テスト用のお気に入りデータフレーム"""
    return pd.DataFrame({
        "削除": [False, False, True],
        "日付": ["2025-01-01", "2025-01-13", "2025-02-11"],
        "祝日名": ["New Year's Day", "Coming of Age Day", "National Foundation Day"],
        "現地名": ["元日", "成人の日", "建国記念の日"],
        "国コード": ["JP", "JP", "JP"]
    })


@pytest.fixture
def sample_search_dataframe():
    """テスト用の検索結果データフレーム"""
    return pd.DataFrame({
        "日付": ["2025-01-01", "2025-01-13"],
        "祝日名": ["New Year's Day", "Coming of Age Day"],
        "現地名": ["元日", "成人の日"],
        "国コード": ["JP", "JP"],
        "お気に入り": [True, False]
    })
