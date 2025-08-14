from typing import List
import pandas as pd
from models import Holiday
import repository
from utils import create_holiday_from_row


def load_favorites() -> List[Holiday]:
    """
    お気に入りの祝日を読み込む

    Returns:
        List[Holiday]: お気に入りの祝日リスト
    """
    try:
        return repository.load_favorites()
    except Exception as e:
        raise Exception(f"お気に入りの読み込みに失敗しました: {str(e)}")


def save_favorites(favorites: List[Holiday]) -> None:
    """
    お気に入りの祝日を保存する

    Args:
        favorites: 保存する祝日のリスト
    """
    try:
        repository.save_favorites(favorites)
    except Exception as e:
        raise Exception(f"お気に入りの保存に失敗しました: {str(e)}")


def remove_selected_favorites(
    current_favorites: List[Holiday], edited_df: pd.DataFrame
) -> List[Holiday]:
    """
    選択された祝日を削除する

    Args:
        current_favorites: 現在のお気に入りリスト
        edited_df: 編集されたデータフレーム

    Returns:
        List[Holiday]: 削除後の祝日リスト
    """
    new_favorites = []
    for idx, row in edited_df.iterrows():
        if not row["削除"]:
            holiday = create_holiday_from_row(row)
            new_favorites.append(holiday)
    return new_favorites


def clear_all_favorites() -> List[Holiday]:
    """
    すべてのお気に入りを削除する

    Returns:
        List[Holiday]: 空のリスト
    """
    return []


def get_favorites_dataframe(favorites: List[Holiday]) -> pd.DataFrame:
    """
    お気に入りリストをデータフレームに変換する

    Args:
        favorites: お気に入りリスト

    Returns:
        pd.DataFrame: データフレーム形式のお気に入りデータ
    """
    # 列名を定義
    columns = ["削除", "日付", "祝日名", "現地名", "国コード"]
    
    if not favorites:
        # 空のリストの場合は列のみのDataFrameを返す
        return pd.DataFrame(columns=columns)
    
    df_data = []
    for holiday in favorites:
        df_data.append(
            {
                "削除": False,
                "日付": holiday.date,
                "祝日名": holiday.name,
                "現地名": holiday.local_name,
                "国コード": holiday.country_code,
            }
        )

    return pd.DataFrame(df_data)


def get_favorites_statistics(favorites: List[Holiday]) -> dict:
    """
    お気に入りの統計情報を取得する

    Args:
        favorites: お気に入りリスト

    Returns:
        dict: 統計情報の辞書
    """
    if not favorites:
        return {}

    df = get_favorites_dataframe(favorites)

    # 国別の統計
    country_stats = df["国コード"].value_counts()

    # 月別の分布
    df["月"] = pd.to_datetime(df["日付"]).dt.month
    month_stats = df["月"].value_counts().sort_index()
    most_month = month_stats.idxmax()

    # 年別の分布
    df["年"] = pd.to_datetime(df["日付"]).dt.year
    year_stats = df["年"].value_counts()

    return {
        "country_stats": country_stats,
        "month_stats": month_stats,
        "year_stats": year_stats,
        "most_month": most_month,
        "total_countries": len(country_stats),
        "total_holidays": len(favorites),
    }


def get_country_grouped_holidays(favorites: List[Holiday]) -> dict:
    """
    国別にグループ化された祝日データを取得する

    Args:
        favorites: お気に入りリスト

    Returns:
        dict: 国別にグループ化された祝日データ
    """
    if not favorites:
        return {}

    df = get_favorites_dataframe(favorites)
    unique_countries = df["国コード"].unique()

    grouped_data = {}
    for country in sorted(unique_countries):
        country_holidays = df[df["国コード"] == country]
        grouped_data[country] = country_holidays[
            ["日付", "祝日名", "現地名"]
        ].sort_values("日付")

    return grouped_data


def update_favorites_from_search(
    current_favorites: List[Holiday],
    edited_df: pd.DataFrame,
    holidays: List[Holiday],
    selected_country_code: str,
) -> List[Holiday]:
    """
    検索結果からお気に入りを更新する（追加のみ、削除は不可）

    Args:
        current_favorites: 現在のお気に入りリスト
        edited_df: 編集されたデータフレーム（お気に入り列を含む）
        holidays: 検索結果の祝日リスト
        selected_country_code: 選択された国コード

    Returns:
        List[Holiday]: 更新後のお気に入りリスト
    """
    # 既存のお気に入りをすべて保持
    new_favorites = list(current_favorites)

    # 検索結果から新規お気に入りを追加
    added_count = 0
    for idx, row in edited_df.iterrows():
        if row["お気に入り"]:
            holiday = create_holiday_from_row(row)

            # 重複チェック（日付、名前、国コードで判定）
            is_duplicate = any(
                existing.date == holiday.date
                and existing.name == holiday.name
                and existing.country_code == holiday.country_code
                for existing in new_favorites
            )

            if not is_duplicate:
                new_favorites.append(holiday)
                added_count += 1

    return new_favorites
