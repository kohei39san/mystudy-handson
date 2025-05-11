# ゲーム情報をDiscordに定期送信するシステム

## 概要

このプロジェクトは、AWS Lambdaを使用して以下のゲーム情報を取得し、Discordに定期的に送信するシステムを構築します：

1. 崩壊スターレイルの期限間近のコード
2. 原神インパクトの期限間近のコード

システムは、期限切れ2週間前のコードを自動的に検出し、Discordウェブフックを通じて通知します。各通知にはコードの自動入力リンクが含まれます。

## アーキテクチャ

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   EventBridge   │────▶│     Lambda      │────▶│     Discord     │
│  (週次スケジュール)  │     │  (Python関数)   │     │   (Webhook)    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │   OpenRouter    │
                      │    (AI API)     │
                      └─────────────────┘
```

### 使用するAWSサービス

- **AWS Lambda**: ゲーム情報を取得しDiscordへ送信するPython関数を実行
- **AWS EventBridge**: 1週間ごとにLambda関数を実行するスケジューラー
- **AWS Systems Manager Parameter Store**: APIキーやWebhook URLなどの機密情報を安全に保存
- **AWS IAM**: 必要な権限を持つロールとポリシーを提供

## デプロイ方法

### 前提条件

- AWS CLIがインストールされ、適切に設定されていること
- Terraformがインストールされていること
- OpenRouter APIキーを取得していること
- Discordウェブフック URLを取得していること

### デプロイ手順

1. 必要なパラメータを設定します：

```bash
# OpenRouter APIキーをSSMパラメータストアに保存
aws ssm put-parameter --name "/game-info/openrouter-api-key" --value "your-api-key" --type SecureString --tier "Standard"

# Discordウェブフック URLをSSMパラメータストアに保存
aws ssm put-parameter --name "/game-info/discord-webhook-url" --value "your-webhook-url" --type SecureString --tier "Standard"
```

2. Terraformを使用してデプロイする前に、必要なPythonモジュールをインストールして`../../lambda_function/package`ディレクトリを準備します：

```bash
cp -r ../scripts/018.send-game-info-to-discord/* ../../lambda_function/
pip install -r ../scripts/018.send-game-info-to-discord/requirements.txt --target ../../lambda_function/
```

3. Terraformを使用してデプロイします：

```bash
cd 018.send-game-info-to-discord
terraform init
terraform plan
terraform apply
```

4. CloudWatch Logsロググループの保持期間を3日に設定します：

```bash
aws logs put-retention-policy --log-group-name "/aws/lambda/GameInfoToDiscordFunction" --retention-in-days 3
```

## 設定パラメータ

Terraformの変数を使用して以下のパラメータをカスタマイズできます：

| パラメータ名 | 説明 | デフォルト値 |
|------------|------|------------|
| `schedule_expression` | Lambda実行スケジュール（cron式） | `cron(0 0 ? * SUN *)` (毎週日曜日午前0時) |
| `lambda_timeout` | Lambda関数のタイムアウト（秒） | `30` |
| `lambda_memory_size` | Lambda関数のメモリサイズ（MB） | `128` |
| `openrouter_api_key_param` | OpenRouter APIキーのSSMパラメータ名 | `/game-info/openrouter-api-key` |
| `discord_webhook_url_param` | DiscordウェブフックURLのSSMパラメータ名 | `/game-info/discord-webhook-url` |

## ローカルでのテスト方法

ローカル環境でスクリプトをテストするには、以下のコマンドを実行します：

```bash
cd scripts/018.send-game-info-to-discord
python local_test.py --api-key "your-openrouter-api-key" --webhook-url "your-discord-webhook-url"
```

オプション：
- `--dry-run`: Discordに実際に送信せずにテストを実行
- `--verbose`: 詳細なログ出力を表示

## トラブルシューティング

### 一般的な問題

1. **Lambda関数がタイムアウトする**
   - `lambda_timeout`パラメータを増やしてください
   - `lambda_memory_size`パラメータを増やしてパフォーマンスを向上させてください

2. **OpenRouter APIエラー**
   - APIキーが正しく設定されているか確認してください
   - APIの利用制限に達していないか確認してください

3. **Discordウェブフックエラー**
   - ウェブフックURLが有効であることを確認してください
   - ウェブフックが設定されているチャンネルが存在することを確認してください

## メンテナンス

- **コードの更新**: Lambda関数のコードを更新する場合は、CloudFormationテンプレートを更新し、Terraformを再適用してください
- **スケジュール変更**: スケジュールを変更するには、`schedule_expression`パラメータを更新してください