# 040.cloudwatch-logs-keyword-search

## 概要

CloudWatch Logsのロググループからキーワードだけでログを検索するPythonスクリプトです。

ロググループ名やロググループのプレフィックスを指定し、検索したいキーワードを渡すだけでログを絞り込むことができます。
複数のロググループを横断して検索することも可能です。

## 機能

- ロググループ名（完全一致）またはプレフィックス（前方一致）でロググループを指定
- キーワードによるログの絞り込み検索（CloudWatch Logs フィルターパターンを使用）
- 相対時刻（例: `1h`, `30m`, `7d`）による検索範囲の指定
- 検索結果の件数上限指定
- AWSリージョンおよびプロファイルの指定

## ディレクトリ構成

```
040.cloudwatch-logs-keyword-search/
├── README.md                         # このファイル
├── pytest.ini                        # pytest設定
└── scripts/
    ├── requirements.txt              # 依存ライブラリ
    └── search_cloudwatch_logs.py     # メインスクリプト
└── tests/
    └── test_search_cloudwatch_logs.py # テストコード
```

## 前提条件

- Python 3.10以降
- AWSアカウントへのアクセス権限（CloudWatch Logs の `logs:DescribeLogGroups`, `logs:FilterLogEvents` アクション）

## セットアップ

```bash
cd 040.cloudwatch-logs-keyword-search
pip install -r scripts/requirements.txt
```

## 使い方

### 基本的な使用方法

```bash
# ロググループ名を完全一致で指定してキーワード検索
python scripts/search_cloudwatch_logs.py \
  --keyword ERROR \
  --log-group-name /aws/lambda/my-function

# プレフィックスに一致する全ロググループを検索
python scripts/search_cloudwatch_logs.py \
  --keyword ERROR \
  --log-group-prefix /aws/lambda/
```

### オプション一覧

| オプション | 説明 | デフォルト |
|---|---|---|
| `--keyword` | 検索するキーワード（必須） | - |
| `--log-group-name` | 検索対象のロググループ名（完全一致） | - |
| `--log-group-prefix` | 検索対象ロググループのプレフィックス | - |
| `--since` | 検索開始時刻（`1h`, `30m`, `7d` 形式） | `1h` |
| `--until` | 検索終了時刻（`1h`, `30m`, `7d` 形式） | 現在時刻 |
| `--limit` | 取得する最大件数 | `100` |
| `--region` | AWSリージョン | 環境変数 or デフォルト |
| `--profile` | AWS CLIプロファイル名 | デフォルトプロファイル |

> `--log-group-name` と `--log-group-prefix` は同時に指定できません。

### 使用例

```bash
# 過去30分のERRORログを/aws/lambda/配下の全グループから検索
python scripts/search_cloudwatch_logs.py \
  --keyword ERROR \
  --log-group-prefix /aws/lambda/ \
  --since 30m

# 過去7日間のログを特定グループから最大50件取得
python scripts/search_cloudwatch_logs.py \
  --keyword "timeout" \
  --log-group-name /aws/ecs/my-service \
  --since 7d \
  --limit 50

# リージョンとプロファイルを明示的に指定
python scripts/search_cloudwatch_logs.py \
  --keyword WARN \
  --log-group-prefix /app/ \
  --region ap-northeast-1 \
  --profile my-aws-profile
```

### 出力形式

```
[2023-11-14T22:13:21.000Z] [/aws/lambda/my-function] [stream-name] ERROR: 予期しないエラーが発生しました
[2023-11-14T22:14:05.000Z] [/aws/lambda/my-function] [stream-name] ERROR: データベース接続に失敗しました

2 件のログが見つかりました。
```

## テスト実行

```bash
cd 040.cloudwatch-logs-keyword-search

# 全テストを実行
pytest

# ユニットテストのみ実行
pytest -m unit

# 詳細出力で実行
pytest -v
```

## トラブルシューティング

### 認証エラーが発生する場合

AWS CLIの認証設定を確認してください。

```bash
aws sts get-caller-identity
```

### ロググループが見つからない場合

プレフィックスやグループ名が正しいか確認してください。

```bash
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/
```

### 検索結果が多すぎる場合

`--since` で検索期間を短くするか、`--limit` で件数を制限してください。
