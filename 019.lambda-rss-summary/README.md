# RSS Feed Summary to Slack

このプロジェクトは、指定したRSSフィードの内容をダウンロードし、OpenRouterを使用して要約し、その結果をSlackに送信するLambda関数を提供します。

## 機能概要

1. EventBridgeのスケジュールに従って定期的にLambda関数が実行されます
2. Lambda関数は指定されたRSSフィードをダウンロードします
3. OpenRouterのAIを使用して、指定されたプロンプトに基づいてRSSフィードの内容を要約します
4. 生成された要約をSlackのWebhookに送信します

## AWS CLIによるデプロイ方法

### 前提条件

- AWS CLIがインストールされていること
- AWS認証情報が設定されていること
- Python 3.9以上がインストールされていること

### デプロイ手順

1. まず、OpenRouterのAPIキーとSlack WebhookのURLをSSM Parameter Storeに保存します：

```bash
# OpenRouter APIキーを保存
aws ssm put-parameter --name "/rss-summary/openrouter-api-key" --type "SecureString" --value "your-openrouter-api-key" --overwrite --tier Standard

# Slack Webhook URLを保存
aws ssm put-parameter --name "/rss-summary/slack-webhook-url" --type "SecureString" --value "your-slack-webhook-url" --overwrite --tier Standard
```

2. Terraformを使用してデプロイする前に、必要なPythonモジュールをインストールして../../lambda_function/packageディレクトリを準備します：

```bash
cp -r ../scripts/019.lambda-rss-summary/* ../../lambda_function_019.lambda-rss-summary/
pip install -r ..\scripts\019.lambda-rss-summary\requirements.txt --target ../../lambda_function_019.lambda-rss-summary/
```

3. Lambda関数のデプロイパッケージを作成します：

```bash
cd scripts/019.lambda-rss-summary
chmod +x deploy.sh
./deploy.sh
```

4. CloudFormationスタックをデプロイします：

```bash
aws cloudformation deploy \
    --template-file src/019.lambda-rss-summary/template.yaml \
    --stack-name rss-summary-stack \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        OpenRouterApiKeyParam="/rss-summary/openrouter-api-key" \
        SlackWebhookUrlParam="/rss-summary/slack-webhook-url" \
        RssFeedUrl="https://aws.amazon.com/about-aws/whats-new/recent/feed/" \
        SummaryPrompt="AWSの新機能の追加を優先事項として、サービスごとに分類して要約してください。要約は1000文字以内にしてください。" \
        ScheduleExpression="cron(0 9 ? * MON-FRI *)" \
        LambdaTimeout=60 \
        LambdaMemorySize=256
```

5. Lambda関数のコードを更新します：

```bash
aws lambda update-function-code \
    --function-name RssSummaryToSlackFunction \
    --zip-file fileb://scripts/019.lambda-rss-summary/lambda_function.zip
```

## CloudFormationのパラメータの説明

| パラメータ名 | 説明 | デフォルト値 |
|------------|------|------------|
| OpenRouterApiKeyParam | OpenRouter APIキーを保存しているSSM Parameter Storeのパラメータ名 | /rss-summary/openrouter-api-key |
| SlackWebhookUrlParam | Slack Webhook URLを保存しているSSM Parameter Storeのパラメータ名 | /rss-summary/slack-webhook-url |
| RssFeedUrl | 要約するRSSフィードのURL | https://aws.amazon.com/about-aws/whats-new/recent/feed/ |
| SummaryPrompt | 要約生成に使用するプロンプト | AWSの新機能の追加を優先事項として、サービスごとに分類して要約してください。要約は1000文字以内にしてください。 |
| ScheduleExpression | Lambda関数を実行するスケジュール式 | cron(0 9 ? * MON-FRI *) (平日の午前9時) |
| LambdaTimeout | Lambda関数のタイムアウト（秒） | 60 |
| LambdaMemorySize | Lambda関数のメモリサイズ（MB） | 256 |

## ローカルでのテスト方法

Lambda関数をローカルでテストするには、以下のコマンドを実行します：

```bash
cd scripts/019.lambda-rss-summary
python local_test.py \
    --api-key "your-openrouter-api-key" \
    --webhook-url "your-slack-webhook-url" \
    --dry-run  # Slackに送信せずにテストする場合
```

## AWS RSSフィードのプロンプト例

AWS RSSフィード（https://aws.amazon.com/about-aws/whats-new/recent/feed/）を使用する場合の効果的なプロンプト例：

```
AWSの新機能の追加を優先事項として、サービスごとに分類して要約してください。
以下のカテゴリに分けて整理してください：
1. コンピューティング（EC2, Lambda, ECS, EKSなど）
2. ストレージ（S3, EBS, EFSなど）
3. データベース（RDS, DynamoDB, Redshiftなど）
4. ネットワーキング（VPC, Route 53, CloudFrontなど）
5. 機械学習・AI（SageMaker, Bedrock, Rekognitionなど）
6. セキュリティ（IAM, GuardDuty, Security Hubなど）
7. その他の重要な更新

各カテゴリでは、最も重要な新機能や改善点を簡潔に説明してください。
特に以下の点に注目してください：
- 新しいサービスや機能のリリース
- 既存サービスの大幅な機能強化
- 新しいリージョンへの対応
- コスト削減につながる変更

要約は1000文字以内にしてください。
```

このプロンプトは、AWS関連の更新情報をサービスカテゴリごとに整理し、新機能の追加を優先的に取り上げるように設計されています。特に重要な更新や機能強化に焦点を当て、簡潔な要約を生成します。