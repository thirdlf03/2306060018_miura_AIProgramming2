import requests
import pandas as pd
from typing import List
from models import Holiday
from pathlib import Path
from utils import convert_api_response_to_holidays
from constants import API_BASE_URL, FAVORITES_CSV_PATH


def get_available_countries() -> List[dict]:
    """
    利用可能な国のリストをAPIから取得

    Returns:
        List[dict]: 国コードと国名を含む辞書のリスト

    Raises:
        requests.RequestException: API呼び出しに失敗した場合
    """
    response = requests.get(f"{API_BASE_URL}/AvailableCountries")
    response.raise_for_status()
    return response.json()


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
    response = requests.get(f"{API_BASE_URL}/PublicHolidays/{year}/{country_code}")
    response.raise_for_status()
    return convert_api_response_to_holidays(response.json())


def load_favorites() -> List[Holiday]:
    """
    CSVファイルからお気に入りの祝日を読み込む

    Returns:
        List[Holiday]: お気に入りの祝日リスト

    Raises:
        Exception: ファイル読み込みに失敗した場合
    """
    csv_path = Path(FAVORITES_CSV_PATH)

    # ファイルが存在しない場合は空のリストを返す
    if not csv_path.exists():
        return []

    df = pd.read_csv(csv_path)
    if df.empty:
        return []

    favorites = []
    for _, row in df.iterrows():
        holiday = Holiday(
            date=row["date"],
            name=row["name"],
            local_name=row["local_name"],
            country_code=row["country_code"],
        )
        favorites.append(holiday)

    return favorites


def save_favorites(favorites: List[Holiday]) -> None:
    """
    お気に入りの祝日をCSVファイルに保存

    Args:
        favorites: 保存する祝日のリスト

    Raises:
        Exception: ファイル保存に失敗した場合
    """
    csv_path = Path(FAVORITES_CSV_PATH)

    # ディレクトリが存在しない場合は作成
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    # 辞書のリストに変換
    data = []
    for holiday in favorites:
        data.append(
            {
                "date": holiday.date,
                "name": holiday.name,
                "local_name": holiday.local_name,
                "country_code": holiday.country_code,
            }
        )

    # DataFrameに変換してCSVに保存
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)


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
    response = requests.get(f"{API_BASE_URL}/NextPublicHolidays/{country_code}")
    response.raise_for_status()
    return convert_api_response_to_holidays(response.json())
