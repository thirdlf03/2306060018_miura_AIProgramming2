"""
favorite_service.pyのテスト
"""

import pytest
import pandas as pd
from unittest.mock import patch
from models import Holiday
from services.favorite_service import (
    load_favorites,
    save_favorites,
    remove_selected_favorites,
    clear_all_favorites,
    get_favorites_dataframe,
    get_favorites_statistics,
    get_country_grouped_holidays,
    update_favorites_from_search,
)


class TestFavoriteService:
    """favorite_service.pyの関数のテスト"""

    @patch("services.favorite_service.repository.load_favorites")
    def test_load_favorites_success(self, mock_repo_load, sample_holidays):
        """お気に入りの読み込み成功テスト"""
        # モックの設定
        mock_repo_load.return_value = sample_holidays

        result = load_favorites()

        assert result == sample_holidays
        mock_repo_load.assert_called_once()

    @patch("services.favorite_service.repository.load_favorites")
    def test_load_favorites_repository_error(self, mock_repo_load):
        """お気に入りの読み込み失敗テスト（リポジトリエラー）"""
        # モックの設定
        mock_repo_load.side_effect = Exception("Repository Error")

        with pytest.raises(
            Exception, match="お気に入りの読み込みに失敗しました: Repository Error"
        ):
            load_favorites()

    @patch("services.favorite_service.repository.save_favorites")
    def test_save_favorites_success(self, mock_repo_save, sample_holidays):
        """お気に入りの保存成功テスト"""
        save_favorites(sample_holidays)

        mock_repo_save.assert_called_once_with(sample_holidays)

    @patch("services.favorite_service.repository.save_favorites")
    def test_save_favorites_repository_error(self, mock_repo_save):
        """お気に入りの保存失敗テスト（リポジトリエラー）"""
        # モックの設定
        mock_repo_save.side_effect = Exception("Repository Error")

        with pytest.raises(
            Exception, match="お気に入りの保存に失敗しました: Repository Error"
        ):
            save_favorites([])

    def test_remove_selected_favorites(
        self, sample_holidays, sample_favorites_dataframe
    ):
        """選択された祝日の削除テスト"""
        result = remove_selected_favorites(sample_holidays, sample_favorites_dataframe)

        # 削除フラグがFalseのものだけが残る
        assert len(result) == 2
        assert result[0].date == "2025-01-01"
        assert result[1].date == "2025-01-13"
        # 削除フラグがTrueのものは除外される
        assert not any(h.date == "2025-02-11" for h in result)

    def test_remove_selected_favorites_all_deleted(self, sample_holidays):
        """すべての祝日が削除される場合のテスト"""
        df = pd.DataFrame(
            {
                "削除": [True, True, True],
                "日付": ["2025-01-01", "2025-01-13", "2025-02-11"],
                "祝日名": [
                    "New Year's Day",
                    "Coming of Age Day",
                    "National Foundation Day",
                ],
                "現地名": ["元日", "成人の日", "建国記念の日"],
                "国コード": ["JP", "JP", "JP"],
            }
        )

        result = remove_selected_favorites(sample_holidays, df)

        assert len(result) == 0

    def test_clear_all_favorites(self):
        """すべてのお気に入り削除テスト"""
        result = clear_all_favorites()

        assert result == []

    def test_get_favorites_dataframe(self, sample_holidays):
        """お気に入りリストのDataFrame変換テスト"""
        result = get_favorites_dataframe(sample_holidays)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

        # 列の確認
        expected_columns = ["削除", "日付", "祝日名", "現地名", "国コード"]
        assert list(result.columns) == expected_columns

        # 削除フラグの確認
        assert (~result["削除"]).all()

        # データの確認
        assert result.iloc[0]["日付"] == "2025-01-01"
        assert result.iloc[0]["祝日名"] == "New Year's Day"
        assert result.iloc[0]["国コード"] == "JP"

    def test_get_favorites_dataframe_empty_list(self):
        """空のお気に入りリストでのDataFrame変換テスト"""
        result = get_favorites_dataframe([])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["削除", "日付", "祝日名", "現地名", "国コード"]

    def test_get_favorites_statistics(self, sample_holidays):
        """お気に入りの統計情報取得テスト"""
        result = get_favorites_statistics(sample_holidays)

        assert "country_stats" in result
        assert "month_stats" in result
        assert "year_stats" in result
        assert "most_month" in result
        assert "total_countries" in result
        assert "total_holidays" in result

        assert result["total_holidays"] == 3
        assert result["total_countries"] == 1
        assert result["most_month"] == 1  # 1月が最多

    def test_get_favorites_statistics_empty_list(self):
        """空のお気に入りリストでの統計情報取得テスト"""
        result = get_favorites_statistics([])

        assert result == {}

    def test_get_country_grouped_holidays(self, sample_holidays):
        """国別グループ化された祝日データ取得テスト"""
        result = get_country_grouped_holidays(sample_holidays)

        assert "JP" in result
        assert len(result["JP"]) == 3

        # 日付順にソートされていることを確認
        dates = result["JP"]["日付"].tolist()
        assert dates == ["2025-01-01", "2025-01-13", "2025-02-11"]

    def test_get_country_grouped_holidays_empty_list(self):
        """空のお気に入りリストでの国別グループ化テスト"""
        result = get_country_grouped_holidays([])

        assert result == {}

    def test_update_favorites_from_search(
        self, sample_holidays, sample_search_dataframe
    ):
        """検索結果からのお気に入り更新テスト"""
        # 既存のお気に入り（異なる国の祝日を含む）
        existing_favorites = [
            Holiday(
                date="2025-12-25",
                name="Christmas Day",
                local_name="クリスマス",
                country_code="US",
            )
        ]

        result = update_favorites_from_search(
            existing_favorites, sample_search_dataframe, sample_holidays, "JP"
        )

        # 既存のUSの祝日は保持される
        assert any(h.country_code == "US" for h in result)
        # 新しく追加されたJPの祝日も含まれる
        assert any(h.country_code == "JP" and h.date == "2025-01-01" for h in result)

    def test_update_favorites_from_search_no_duplicates(self, sample_holidays):
        """重複チェック付きのお気に入り更新テスト"""
        # 既存のお気に入り
        existing_favorites = [
            Holiday(
                date="2025-01-01",
                name="New Year's Day",
                local_name="元日",
                country_code="JP",
            )
        ]

        # 検索結果（同じ祝日を含む）
        search_df = pd.DataFrame(
            {
                "日付": ["2025-01-01"],
                "祝日名": ["New Year's Day"],
                "現地名": ["元日"],
                "国コード": ["JP"],
                "お気に入り": [True],
            }
        )

        result = update_favorites_from_search(
            existing_favorites, search_df, sample_holidays[:1], "JP"
        )

        # 重複は追加されない
        jp_holidays = [h for h in result if h.country_code == "JP"]
        assert len(jp_holidays) == 1
