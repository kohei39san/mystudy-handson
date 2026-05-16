# 042. AWS Credits Apply

AWS プロモーションクレジットコードを一括適用するスクリプトです。  
新規に起動した Chrome / Microsoft Edge で手動ログインを待機し、`config/credits.csv` に記載されたコードを順番に適用します。  
Management Account で適用すれば、Organization の Credit Sharing 設定によりメンバーアカウントにも自動で適用されます。

## ディレクトリ構成

```
042.aws-credits-apply/
├── scripts/
│   └── apply_credits.py   # メインスクリプト
├── config/
│   └── credits.csv        # 適用するクレジットコード一覧
├── tests/
│   └── test-spec.md       # 単体テスト仕様書
├── logs/                  # 実行結果ログ（自動生成）
└── requirements.txt
```

## 前提条件

- Python 3.11 以上
- Google Chrome または Microsoft Edge がインストール済みであること
- `.env` にログイン開始 URL（`LOGIN_URL`）を設定すること

## セットアップ

```powershell
cd 042.aws-credits-apply
pip install -r requirements.txt
playwright install chromium
```

`.env.example` を `.env` にコピーして設定します。

```powershell
Copy-Item .env.example .env
```

`.env` 設定例:

```dotenv
LOGIN_URL=https://signin.aws.amazon.com/signin
READY_URL=https://us-east-1.console.aws.amazon.com/costmanagement/home?region=us-east-1#/credits/redeemCredits
BROWSER_CHANNEL=chrome
LOGIN_TIMEOUT_MS=300000
```

### READY_URL の実運用パターン例

`READY_URL` は Playwright の URL マッチとして評価されます。  
固定 URL の厳密一致だけでなく、`*` / `**` を使ったパターン指定も可能です。

**1. 厳密一致（推奨: URL が固定の環境）**

```dotenv
READY_URL=https://us-east-1.console.aws.amazon.com/costmanagement/home?region=us-east-1#/credits/redeemCredits
```

**2. クエリ差分を吸収（リージョンや付加パラメータが変わる場合）**

```dotenv
READY_URL=https://us-east-1.console.aws.amazon.com/costmanagement/home*
```

**3. SSO 後の着地点を吸収（パス配下の遷移を許容）**

```dotenv
READY_URL=**/costmanagement/home*
```

**4. 特定アカウントのコンソール配下を待機（着地点が変わる組織向け）**

```dotenv
READY_URL=**.console.aws.amazon.com/**
```

> ヒント: まずは厳密一致で運用し、SSO や組織設定で URL 変動がある場合のみワイルドカードを広げると、意図しないページで待機解除されるリスクを下げられます。

## 使い方

### 1. クレジットコードを記載

`config/credits.csv` に 1 行 1 コードで記載します。  
`#` で始まる行と空行は無視されます。

```
# 2026年5月分
CODE-AAAA-BBBB-CCCC
CODE-DDDD-EEEE-FFFF

# 追加分
CODE-GGGG-HHHH-IIII
```

### 2. スクリプト実行

```powershell
python scripts/apply_credits.py
```

起動したブラウザで手動ログイン（MFA / SSO 含む）を完了してください。  
いずれかのタブの URL が `READY_URL` に一致した時点で自動的にクレジット適用処理を開始します。

> 補足: ログイン後に別タブで AWS コンソールが開く導線でも、READY_URL に一致したタブを検知できます。

**実行例:**
```
クレジットコード 3 件を読み込みました: config/credits.csv
--------------------------------------------------
[1/3] 適用中: 'CODE-AAAA-BBBB-CCCC' ... HTTP 200 → SUCCESS
[2/3] 適用中: 'CODE-DDDD-EEEE-FFFF' ... HTTP 400 → FAILED
[3/3] 適用中: 'CODE-GGGG-HHHH-IIII' ... HTTP 200 → SUCCESS
--------------------------------------------------
  合計    : 3 件
  成功    : 2 件
  失敗    : 1 件
  ログ    : logs/credit_application_20260516_120000.json
```

## ログファイル

実行結果は `logs/credit_application_<YYYYMMDD_HHMMSS>.json` に保存されます。

```json
[
  {
    "code": "CODE-AAAA-BBBB-CCCC",
    "http_status": 200,
    "status": "success",
    "error": null,
    "timestamp": "2026-05-16T12:00:00.000000"
  },
  {
    "code": "CODE-DDDD-EEEE-FFFF",
    "http_status": 400,
    "status": "failed",
    "error": null,
    "timestamp": "2026-05-16T12:00:03.000000"
  }
]
```

| status    | 説明                                        |
|-----------|---------------------------------------------|
| `success` | HTTP 200 が返り、適用成功                   |
| `failed`  | HTTP 4xx/5xx が返り、適用失敗（重複コード含む） |
| `timeout` | 15 秒以内に API レスポンスが返らなかった    |
| `error`   | 予期しない例外が発生した                    |

## 単体テスト仕様

単体テスト仕様書は [tests/test-spec.md](tests/test-spec.md) を参照してください。
