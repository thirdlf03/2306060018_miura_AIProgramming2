# テスト実行ガイド

このディレクトリには、世界の祝日アプリケーションのテストファイルが含まれています。

## テストファイル構成

- `conftest.py` - 共通のフィクスチャと設定
- `test_models.py` - Holidayモデルのテスト
- `test_utils.py` - ユーティリティ関数のテスト
- `test_repository.py` - リポジトリ層のテスト
- `test_holiday_service.py` - 祝日サービスのテスト
- `test_favorite_service.py` - お気に入りサービスのテスト
- `test_quiz_service.py` - クイズサービスのテスト

## テストの実行方法

### 全テストの実行
```bash
pytest
```

### 特定のテストファイルの実行
```bash
pytest tests/test_models.py
```

### 特定のテストクラスの実行
```bash
pytest tests/test_models.py::TestHoliday
```

### 特定のテストメソッドの実行
```bash
pytest tests/test_models.py::TestHoliday::test_holiday_creation
```

### カバレッジ付きでテスト実行
```bash
pytest --cov=. --cov-report=html
```

## テストの特徴

### モックの使用
- 外部API呼び出しは`unittest.mock.patch`を使用してモック化
- ファイルI/O操作も適切にモック化
- データベース操作の代わりにインメモリデータを使用

### フィクスチャ
- `conftest.py`で共通のテストデータを定義
- 各テストで再利用可能なサンプルデータを提供

### エラーケースのテスト
- 正常系だけでなく、例外発生時の動作もテスト
- APIエラー、ファイル読み込みエラーなどのエッジケースをカバー

## テストデータ

テストでは以下のサンプルデータを使用：

- **祝日データ**: 日本の祝日（元日、成人の日、建国記念の日）
- **国データ**: 日本、アメリカ、ドイツ
- **APIレスポンス**: 実際のAPIレスポンス形式に準拠

## カバレッジ

テスト実行後、`htmlcov/`ディレクトリにHTML形式のカバレッジレポートが生成されます。
ブラウザで`htmlcov/index.html`を開いてカバレッジを確認できます。

## 注意事項

- Streamlitの`@st.cache_data`デコレータはテスト環境では無効化されます
- 外部APIへの実際の呼び出しは行われません
- テストデータは日本語と英語の両方を含みます
