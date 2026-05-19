# 単体テスト仕様書

対象: `scripts/apply_credits.py`

> モック対象: `playwright.Page`, `playwright.Response`, `playwright.chromium.launch`, `Path.open`, `Path.mkdir`, `json.dump`, `dotenv.load_dotenv`

## 正常系

> モック対象: `playwright.Page`, `playwright.Response`

| # | テストケース | 入力 | 期待結果 |
|---|------------|------|---------|
| T01 | 有効なクレジットコードを 1 件適用 | 未使用の有効コード 1 件 | `status: success`, `http_status: 200` |
| T02 | 有効なクレジットコードを複数件適用 | 未使用の有効コード 3 件 | 全件 `status: success` |
| T03 | コードとコードの間に待機が入ること | 有効コード 2 件 | 2 件目の開始が 3 秒以上後であること |

## 異常系（コードのスキップと続行）

> モック対象: `playwright.Page`, `playwright.Response`

| # | テストケース | 入力 | 期待結果 |
|---|------------|------|---------|
| T04 | 無効なクレジットコード | 存在しないコード | `status: failed`, `http_status: 4xx` |
| T05 | 既に適用済みのコード | 重複コード | `status: failed`, `http_status: 4xx` |
| T06 | 有効コードと無効コードの混在 | 有効 1 件 + 無効 1 件 | 有効: `success`、無効: `failed`、処理が継続すること |
| T07 | API レスポンスタイムアウト | （ネットワーク遮断など） | `status: timeout`、次のコードの処理に進むこと |

## 境界値

> モック対象: `Path.open`, `playwright.Page`, `playwright.Response`

| # | テストケース | 入力 | 期待結果 |
|---|------------|------|---------|
| T15 | クレジットコードが 1 件だけの場合 | `credits.csv` に有効コード 1 行のみ | 1 件だけ処理され、`status: success` になること |
| T16 | クレジットコード件数が多い場合 | `credits.csv` に有効コード 100 行 | 100 件すべて処理され、途中で停止しないこと |

## CSV 読み込み

> モック対象: `Path.open`

| # | テストケース | 入力 | 期待結果 |
|---|------------|------|---------|
| T08 | `#` で始まるコメント行は無視される | `# コメント\nCODE-XXXX` | コメント行を除く 1 件のみ処理 |
| T09 | 空行は無視される | `CODE-AAAA\n\nCODE-BBBB` | 2 件のみ処理 |
| T10 | credits.csv が存在しない | ファイルなし | エラーメッセージを表示してスクリプト終了 |
| T11 | credits.csv にコードが 0 件 | コメントと空行のみ | 警告メッセージを表示してスクリプト終了 |

## ブラウザ接続

> モック対象: `playwright.chromium.launch`, `playwright.Page.wait_for_url`

| # | テストケース | 入力 | 期待結果 |
|---|------------|------|---------|
| T12 | LOGIN_URL が未設定 | `.env` に `LOGIN_URL` なし | 設定エラーを表示してスクリプト終了 |
| T17 | ログイン完了 URL 待機がタイムアウト | MFA/SSO 完了後も `READY_URL` に一致しない | タイムアウトエラーを表示してスクリプト終了 |
| T18 | 別タブで READY_URL が開かれる | ログイン後に別タブで AWS コンソールが表示 | 一致したタブを検知してクレジット適用処理へ進む |

## ログ出力

> モック対象: `Path.mkdir`, `json.dump`

| # | テストケース | 入力 | 期待結果 |
|---|------------|------|---------|
| T13 | 実行後にログファイルが生成される | 任意のコード 1 件以上 | `logs/credit_application_<timestamp>.json` が生成されること |
| T14 | ログに全コードの結果が記録される | 有効 1 件 + 無効 1 件 | JSON に 2 件分の結果が含まれること |
