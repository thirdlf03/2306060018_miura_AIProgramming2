"""
utils.pyのテスト
"""

import pytest
import pandas as pd
from models import Holiday
from utils import create_holiday_from_row, convert_api_response_to_holidays


class TestUtils:
    """utils.pyの関数のテスト"""

    def test_create_holiday_from_row(self):
        """データフレームの行からHolidayオブジェクトを作成するテスト"""
        # テスト用のデータフレーム行を作成
        row_data = {
            "日付": "2025-01-01",
            "祝日名": "New Year's Day",
            "現地名": "元日",
            "国コード": "JP",
        }
        row = pd.Series(row_data)

        holiday = create_holiday_from_row(row)

        assert isinstance(holiday, Holiday)
        assert holiday.date == "2025-01-01"
        assert holiday.name == "New Year's Day"
        assert holiday.local_name == "元日"
        assert holiday.country_code == "JP"

    def test_create_holiday_from_row_with_different_data(self):
        """異なるデータでのHolidayオブジェクト作成テスト"""
        row_data = {
            "日付": "2025-12-25",
            "祝日名": "Christmas Day",
            "現地名": "クリスマス",
            "国コード": "US",
        }
        row = pd.Series(row_data)

        holiday = create_holiday_from_row(row)

        assert holiday.date == "2025-12-25"
        assert holiday.name == "Christmas Day"
        assert holiday.local_name == "クリスマス"
        assert holiday.country_code == "US"

    def test_convert_api_response_to_holidays(self):
        """APIレスポンスをHolidayオブジェクトのリストに変換するテスト"""
        api_response = [
            {
                "date": "2025-01-01",
                "name": "New Year's Day",
                "localName": "元日",
                "countryCode": "JP",
            },
            {
                "date": "2025-01-13",
                "name": "Coming of Age Day",
                "localName": "成人の日",
                "countryCode": "JP",
            },
        ]

        holidays = convert_api_response_to_holidays(api_response)

        assert len(holidays) == 2
        assert all(isinstance(h, Holiday) for h in holidays)

        # 最初の祝日をチェック
        assert holidays[0].date == "2025-01-01"
        assert holidays[0].name == "New Year's Day"
        assert holidays[0].local_name == "元日"
        assert holidays[0].country_code == "JP"

        # 2番目の祝日をチェック
        assert holidays[1].date == "2025-01-13"
        assert holidays[1].name == "Coming of Age Day"
        assert holidays[1].local_name == "成人の日"
        assert holidays[1].country_code == "JP"

    def test_convert_api_response_to_holidays_empty_list(self):
        """空のAPIレスポンスの変換テスト"""
        api_response = []

        holidays = convert_api_response_to_holidays(api_response)

        assert isinstance(holidays, list)
        assert len(holidays) == 0

    def test_convert_api_response_to_holidays_single_item(self):
        """単一アイテムのAPIレスポンスの変換テスト"""
        api_response = [
            {
                "date": "2025-02-11",
                "name": "National Foundation Day",
                "localName": "建国記念の日",
                "countryCode": "JP",
            }
        ]

        holidays = convert_api_response_to_holidays(api_response)

        assert len(holidays) == 1
        assert holidays[0].date == "2025-02-11"
        assert holidays[0].name == "National Foundation Day"
        assert holidays[0].local_name == "建国記念の日"
        assert holidays[0].country_code == "JP"

    def test_convert_api_response_to_holidays_with_special_characters(self):
        """特殊文字を含むAPIレスポンスの変換テスト"""
        api_response = [
            {
                "date": "2025-05-05",
                "name": "Children's Day",
                "localName": "こどもの日",
                "countryCode": "JP",
            }
        ]

        holidays = convert_api_response_to_holidays(api_response)

        assert len(holidays) == 1
        assert holidays[0].name == "Children's Day"
        assert holidays[0].local_name == "こどもの日"
