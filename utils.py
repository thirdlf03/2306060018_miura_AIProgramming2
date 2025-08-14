import pandas as pd
from typing import List
from models import Holiday


def create_holiday_from_row(row: pd.Series) -> Holiday:
    """
    データフレームの行からHolidayオブジェクトを作成する

    Args:
        row: データフレームの行

    Returns:
        Holiday: 作成されたHolidayオブジェクト
    """
    return Holiday(
        date=row["日付"],
        name=row["祝日名"],
        local_name=row["現地名"],
        country_code=row["国コード"],
    )


def convert_api_response_to_holidays(api_response: List[dict]) -> List[Holiday]:
    """
    APIレスポンスをHolidayオブジェクトのリストに変換する

    Args:
        api_response: APIからのレスポンス（辞書のリスト）

    Returns:
        List[Holiday]: Holidayオブジェクトのリスト
    """
    holidays = []
    for holiday_data in api_response:
        holiday = Holiday(
            date=holiday_data["date"],
            name=holiday_data["name"],
            local_name=holiday_data["localName"],
            country_code=holiday_data["countryCode"],
        )
        holidays.append(holiday)
    return holidays
