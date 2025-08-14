"""祝日関連のビジネスロジック"""

from typing import List
from models import Holiday
import pandas as pd
import streamlit as st
import repository
from constants import API_CACHE_TTL


@st.cache_data(ttl=API_CACHE_TTL)
def get_available_countries() -> List[dict]:
    """
    利用可能な国のリストをAPIから取得

    Returns:
        List[dict]: 国コードと国名を含む辞書のリスト

    Raises:
        requests.RequestException: API呼び出しに失敗した場合
    """
    try:
        return repository.get_available_countries()
    except Exception as e:
        # 例外を再発生させる
        raise e


@st.cache_data(ttl=API_CACHE_TTL)
def get_public_holidays(year: int, country_code: str) -> List[Holiday]:
    """
    指定された年と国の祝日一覧をAPIから取得

    Args:
        year: 年（例: 2025）
        country_code: 国コード（例: "JP"）

    Returns:
        List[Holiday]: 祝日のリスト

    Raises:
        requests.RequestException: API呼び出しに失敗した場合
    """
    return repository.get_public_holidays(year, country_code)


@st.cache_data(ttl=API_CACHE_TTL)
def get_next_public_holidays(country_code: str) -> List[Holiday]:
    """
    指定された国の今後の祝日を取得

    Args:
        country_code: 国コード（例: "JP"）

    Returns:
        List[Holiday]: 祝日のリスト

    Raises:
        requests.RequestException: API呼び出しに失敗した場合
    """
    return repository.get_next_public_holidays(country_code)


def get_country_options() -> dict:
    """
    国選択用のオプション辞書を生成

    Returns:
        dict: 表示名をキー、国コードを値とする辞書
    """
    try:
        countries = get_available_countries()
        if countries:
            return {
                f"{country['name']} ({country['countryCode']})": country["countryCode"]
                for country in countries
            }
    except Exception:
        pass
    return {}


def holidays_to_search_dataframe(
    holidays: List[Holiday], favorites: List[Holiday]
) -> pd.DataFrame:
    """
    検索結果用のDataFrameを生成（お気に入り状態付き）

    Args:
        holidays: 祝日のリスト
        favorites: お気に入りのリスト

    Returns:
        pd.DataFrame: 検索結果用のデータフレーム
    """
    # 列名を定義
    columns = ["日付", "祝日名", "現地名", "国コード", "お気に入り"]

    if not holidays:
        # 空のリストの場合は列のみのDataFrameを返す
        return pd.DataFrame(columns=columns)

    df_data = []
    for holiday in holidays:
        is_favorite = holiday in favorites
        df_data.append(
            {
                "日付": holiday.date,
                "祝日名": holiday.name,
                "現地名": holiday.local_name,
                "国コード": holiday.country_code,
                "お気に入り": is_favorite,
            }
        )
    return pd.DataFrame(df_data)
