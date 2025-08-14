## Nager.Date API - V3
Nager.Date はオープンソースの祝日APIです。

## エンドポイント

### Country

#### GET `/api/v3/CountryInfo/{countryCode}`
- **概要**: 指定した国の情報を取得
- **operationId**: `CountryCountryInfo`
- **パスパラメータ**
  - `countryCode` (string, 必須): 国コード ISO 3166-1 alpha-2
- **レスポンス**
  - 200 OK: `CountryInfoDto`

#### GET `/api/v3/AvailableCountries`
- **概要**: 利用可能なすべての国を取得
- **operationId**: `CountryAvailableCountries`
- **レスポンス**
  - 200 OK: `CountryV3Dto` の配列

### LongWeekend

#### GET `/api/v3/LongWeekend/{year}/{countryCode}`
- **概要**: 指定した国のロングウィークエンドを取得
- **operationId**: `LongWeekendLongWeekend`
- **パスパラメータ**
  - `year` (integer, int32, 必須)
  - `countryCode` (string, 必須): 国コード ISO 3166-1 alpha-2
- **クエリパラメータ**
  - `availableBridgeDays` (integer, int32, 省略可, 既定値: 1)
  - `subdivisonCode` (string, 省略可)
- **レスポンス**
  - 200 OK: `LongWeekendV3Dto` の配列

### PublicHoliday

#### GET `/api/v3/PublicHolidays/{year}/{countryCode}`
- **概要**: 祝日の一覧を取得
- **operationId**: `PublicHolidayPublicHolidaysV3`
- **パスパラメータ**
  - `year` (integer, int32, 必須)
  - `countryCode` (string, 必須): 国コード ISO 3166-1 alpha-2
- **レスポンス**
  - 200 Public holidays: `PublicHolidayV3Dto` の配列
  - 400 Validation failure
  - 404 CountryCode is unknown

#### GET `/api/v3/IsTodayPublicHoliday/{countryCode}`
- **概要**: 本日が祝日かを判定（UTC基準。オフセット指定可）
- **operationId**: `PublicHolidayIsTodayPublicHoliday`
- **説明**: 計算はUTC基準。`offset` で調整可能。`curl` 用の特別なエンドポイント。
  - 200: 本日は祝日
  - 204: 本日は祝日ではない
- **パスパラメータ**
  - `countryCode` (string, 必須): 国コード ISO 3166-1 alpha-2
- **クエリパラメータ**
  - `countyCode` (string, 省略可): サブディビジョンコード（ISO-3166-2）
  - `offset` (integer, int32, 省略可, 既定値: 0, 最小: -12, 最大: 12): UTCタイムゾーンオフセット
- **レスポンス**
  - 200 Today is a public holiday
  - 204 Today is not a public holiday
  - 400 Validation failure
  - 404 CountryCode is unknown
- **使用例**
```bash
STATUSCODE=$(curl --silent --output /dev/stderr --write-out "%{http_code}" \
  https://date.nager.at/Api/v3/IsTodayPublicHoliday/AT)
if [ "$STATUSCODE" -ne 200 ]; then
  # error handling
  exit 1
fi
```

#### GET `/api/v3/NextPublicHolidays/{countryCode}`
- **概要**: 指定した国の今後365日分の祝日を取得
- **operationId**: `PublicHolidayNextPublicHolidays`
- **パスパラメータ**
  - `countryCode` (string, 必須): 国コード ISO 3166-1 alpha-2
- **レスポンス**
  - 200 OK: `PublicHolidayV3Dto` の配列

#### GET `/api/v3/NextPublicHolidaysWorldwide`
- **概要**: 今後7日間の世界の祝日を取得
- **operationId**: `PublicHolidayNextPublicHolidaysWorldwide`
- **レスポンス**
  - 200 OK: `PublicHolidayV3Dto` の配列

### Version

#### GET `/api/v3/Version`
- **概要**: 稼働中の Nager.Date ライブラリのバージョン情報を取得
- **operationId**: `VersionGetVersion`
- **レスポンス**
  - 200 OK: `VersionInfoDto`

## スキーマ

### `CountryInfoDto` (object)
- **説明**: CountryInfo Dto
- **required**: `commonName`, `officialName`, `countryCode`, `region`
- **properties**
  - `commonName` (string, nullable): CommonName
  - `officialName` (string, nullable): OfficialName
  - `countryCode` (string, nullable): CountryCode
  - `region` (string, nullable): Region
  - `borders` (array, nullable): Country Borders。要素は `CountryInfoDto`
- **additionalProperties**: false

### `CountryV3Dto` (object)
- **説明**: Country
- **required**: `countryCode`, `name`
- **properties**
  - `countryCode` (string, nullable): Country Code
  - `name` (string, nullable): Country Name
- **additionalProperties**: false

### `HolidayTypes` (string enum)
- **値**: `Public` | `Bank` | `School` | `Authorities` | `Optional` | `Observance`

### `LongWeekendV3Dto` (object)
- **説明**: Long Weekend
- **properties**
  - `startDate` (string, format: date): Start Date
  - `endDate` (string, format: date): End Date
  - `dayCount` (integer, int32): Day Count
  - `needBridgeDay` (boolean): Need Bridge Day
  - `bridgeDays` (array, nullable): 連休化に必要なブリッジ休日。要素は `string` (format: date)
- **additionalProperties**: false

### `PublicHolidayV3Dto` (object)
- **説明**: Public Holiday
- **required**: `countryCode`, `localName`, `name`, `types`
- **properties**
  - `date` (string, format: date): The date
  - `localName` (string, nullable): Local name
  - `name` (string, nullable): English name
  - `countryCode` (string, nullable): ISO 3166-1 alpha-2
  - `fixed` (boolean, deprecated): Is this public holiday every year on the same date
  - `global` (boolean): Is this public holiday in every county (federal state)
  - `counties` (array, nullable): ISO-3166-2 - Federal states。要素は `string`
  - `launchYear` (integer, int32, nullable): The launch year of the public holiday
  - `types` (array, nullable): この祝日に該当する種別。要素は `HolidayTypes`
- **additionalProperties**: false

### `VersionInfoDto` (object)
- **説明**: Version Info Dto
- **required**: `name`, `version`
- **properties**
  - `name` (string, nullable): Name
  - `version` (string, nullable): Version
- **additionalProperties**: false

## 備考
- レスポンスの `content` で `text/plain`, `application/json`, `text/json` が定義されていますが、通常は `application/json` を利用します。
- `IsTodayPublicHoliday` の判定はUTC基準です。ローカルタイムでの判定が必要な場合は `offset` を設定してください。
- `countyCode`/`subdivisonCode` はサブディビジョン（州・県等）のコードを指します（ISO-3166-2）。


