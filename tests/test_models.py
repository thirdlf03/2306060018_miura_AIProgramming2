"""
models.pyのテスト
"""

import pytest
from models import Holiday


class TestHoliday:
    """Holidayクラスのテスト"""

    def test_holiday_creation(self):
        """祝日オブジェクトの作成テスト"""
        holiday = Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="JP",
        )

        assert holiday.date == "2025-01-01"
        assert holiday.name == "New Year's Day"
        assert holiday.local_name == "元日"
        assert holiday.country_code == "JP"

    def test_holiday_equality_same_data(self):
        """同じデータを持つ祝日の等価性テスト"""
        holiday1 = Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="JP",
        )
        holiday2 = Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="JP",
        )

        assert holiday1 == holiday2

    def test_holiday_equality_different_names(self):
        """異なる名前を持つ祝日の等価性テスト（日付と国コードが同じ）"""
        holiday1 = Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="JP",
        )
        holiday2 = Holiday(
            date="2025-01-01",
            name="Different Name",
            local_name="異なる名前",
            country_code="JP",
        )

        assert holiday1 == holiday2  # 日付と国コードが同じなので等価

    def test_holiday_equality_different_dates(self):
        """異なる日付を持つ祝日の等価性テスト"""
        holiday1 = Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="JP",
        )
        holiday2 = Holiday(
            date="2025-01-13",
            name="New Year's Day",
            local_name="元日",
            country_code="JP",
        )

        assert holiday1 != holiday2  # 日付が異なるので不等価

    def test_holiday_equality_different_countries(self):
        """異なる国コードを持つ祝日の等価性テスト"""
        holiday1 = Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="JP",
        )
        holiday2 = Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="US",
        )

        assert holiday1 != holiday2  # 国コードが異なるので不等価

    def test_holiday_equality_with_non_holiday(self):
        """Holiday以外のオブジェクトとの等価性テスト"""
        holiday = Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="JP",
        )

        assert holiday != "not a holiday"
        assert holiday != 123
        assert holiday != None

    def test_holiday_hash(self):
        """祝日のハッシュ値テスト"""
        holiday1 = Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="JP",
        )
        holiday2 = Holiday(
            date="2025-01-01",
            name="Different Name",
            local_name="異なる名前",
            country_code="JP",
        )

        # 同じ日付と国コードを持つ祝日は同じハッシュ値を持つ
        assert hash(holiday1) == hash(holiday2)

    def test_holiday_in_set(self):
        """セットでの重複除去テスト"""
        holiday1 = Holiday(
            date="2025-01-01",
            name="New Year's Day",
            local_name="元日",
            country_code="JP",
        )
        holiday2 = Holiday(
            date="2025-01-01",
            name="Different Name",
            local_name="異なる名前",
            country_code="JP",
        )
        holiday3 = Holiday(
            date="2025-01-13",
            name="Coming of Age Day",
            local_name="成人の日",
            country_code="JP",
        )

        holiday_set = {holiday1, holiday2, holiday3}
        # holiday1とholiday2は同じ日付と国コードなので、セットでは1つとして扱われる
        assert len(holiday_set) == 2
