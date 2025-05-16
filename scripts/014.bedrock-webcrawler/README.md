# Bedrock Web Crawler ローカルテストツール

このディレクトリには、Amazon Bedrock Web Crawlerをローカルからテストするためのスクリプトが含まれています。

## ファイル構成

- `local_test.py`: ローカルからBedrockウェブクローラーを実行するためのPythonスクリプト
- `crawl_handler.py`: Lambda関数のハンドラー
- `crawl_utils.py`: クロール関連のユーティリティ関数
- `init-opensearch.sh`: OpenSearchインデックスを初期化するためのシェルスクリプト

## 前提条件

1. Python 3.8以上
2. AWS CLIがインストールされ、適切に設定されていること
3. 必要なPythonパッケージ:
   ```
   pip install boto3
   ```
4. Bedrockサービスへのアクセス権限を持つIAMユーザーまたはロール

## local_test.py の使用方法

### 基本的な使用方法

```bash
python local_test.py --data-source-id <BEDROCK_DATA_SOURCE_ID>
```

これにより、指定されたBedrockデータソースに対して新しいクロールが開始されます。

### オプション

- `--region`: AWSリージョンを指定（デフォルト: ap-northeast-1）
- `--profile`: 使用するAWS CLIプロファイルを指定
- `--data-source-id`: BedrockデータソースのID（必須）
- `--wait`: クロールの完了を待つ
- `--timeout`: 完了を待つ最大時間（秒）（デフォルト: 300秒）

### 例

```bash
# クロールを開始し、完了を待つ
python local_test.py --data-source-id ds-12345abcde --wait

# 特定のプロファイルとリージョンを使用
python local_test.py --data-source-id ds-12345abcde --profile myprofile --region us-east-1

# タイムアウトを10分に設定
python local_test.py --data-source-id ds-12345abcde --wait --timeout 600
```

## 戻り値

スクリプトは以下の終了コードを返します：

- `0`: 成功
- `1`: エラー

## エラーハンドリング

エラーが発生した場合、スクリプトはエラーメッセージを表示して終了します。一般的なエラーには以下が含まれます：

- 無効なデータソースID
- AWS認証情報の問題
- Bedrockサービスへのアクセス権限の不足
- ネットワークの問題

## ログ

スクリプトは標準出力に進行状況とエラーメッセージを出力します。詳細なログが必要な場合は、AWS CLIの設定で適切なログレベルを設定してください。