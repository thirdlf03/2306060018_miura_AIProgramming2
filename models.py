from dataclasses import dataclass


@dataclass
class Holiday:
    """祝日を表すデータクラス"""

    date: str  # YYYY-MM-DD形式
    name: str
    local_name: str
    country_code: str

    def __eq__(self, other):
        """お気に入り重複チェック用の等価性判定"""
        if not isinstance(other, Holiday):
            return False
        return self.date == other.date and self.country_code == other.country_code

    def __hash__(self):
        """セットやディクショナリで使用するためのハッシュ値"""
        return hash((self.date, self.country_code))
