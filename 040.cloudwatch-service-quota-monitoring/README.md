# Trusted Advisor Refresh and Slack Notification (No SNS, No CloudWatch Alarms)

Trusted Advisorチェックを定期的にリフレッシュし、リフレッシュ後に発行されるイベントをAWS User Notificationsで検知してSlackへ通知します。

この構成では、SNSおよびCloudWatchアラームは作成しません。

ステートマシン定義はテンプレートへ埋め込まず、asl/trusted-advisor-refresh.asl.json を利用します。

## 概要

このCloudFormationテンプレートは以下を作成します。

- Trusted Advisorリフレッシュワークフロー
  - EventBridgeスケジュールルール
  - Step Functionsステートマシン
  - 必要IAMロール
- Trusted Advisor リフレッシュイベントのSlack通知（AWS User Notifications）
  - NotificationConfiguration
  - ChannelAssociation
  - EventRule

## 有効条件

### Trusted Advisorリフレッシュワークフロー

次の条件を満たす場合に作成されます。

- TrustedAdvisorCheckIds を指定している
- TrustedAdvisorDefinitionS3Bucket / TrustedAdvisorDefinitionS3Key が設定されている
- スタックのデプロイ先リージョンが us-east-1

### Trusted AdvisorイベントのSlack通知

次の条件を満たす場合に作成されます。

- TrustedAdvisorSlackChannelArn を指定している
- スタックのデプロイ先リージョンが us-east-1

## 前提条件

- AWS CLIがインストールされていること
- 適切なIAM権限があること
  - cloudformation:*
  - events:*
  - states:*
  - iam:*
  - logs:*
  - support:RefreshTrustedAdvisorCheck
  - notifications:*
  - s3:GetObject
  - s3:PutObject
- StackSetとして使用する場合:
  - AWS Organizationsが有効化されていること、または管理アカウントでのStackSet権限があること

Trusted Advisorに関する注意:
- 自動更新・全チェック利用・EventBridge連携は Business系以上のサポートプランが前提です。

## パラメータ

| パラメータ | 説明 | デフォルト値 |
|----------|------|------------|
| TrustedAdvisorRefreshSchedule | TAリフレッシュの定期実行式 | rate(6 hours) |
| TrustedAdvisorCheckIds | リフレッシュ対象TAチェックID（カンマ区切り） | (空) |
| TrustedAdvisorDefinitionS3Bucket | ASL定義ファイルのS3バケット | (空) |
| TrustedAdvisorDefinitionS3Key | ASL定義ファイルのS3キー | (空) |
| TrustedAdvisorSlackChannelArn | AWS User Notificationsの通知先SlackチャネルARN | (空) |
| TrustedAdvisorNotificationRegions | AWS User Notifications EventRule の対象リージョン（カンマ区切り） | us-east-1,us-east-2,us-west-2,eu-west-1,eu-central-1,ap-northeast-1,ap-southeast-1,ap-southeast-2,ap-south-1,ca-central-1,sa-east-1 |

## デプロイ方法

### 1. スクリプトを使用したデプロイ（単一アカウント）

```bash
cd scripts

# 基本的なデプロイ（Slack通知のみ）
AWS_DEFAULT_REGION=us-east-1 \
TRUSTED_ADVISOR_SLACK_CHANNEL_ARN=arn:aws:chatbot:us-east-1:123456789012:chat-configuration/slack-channel/my-channel \
./deploy.sh deploy-stack

# TAリフレッシュ + Slack通知を有効化（us-east-1必須）
AWS_DEFAULT_REGION=us-east-1 \
TRUSTED_ADVISOR_CHECK_IDS=eW7HH0l7J9,c1z7kmr03n \
TRUSTED_ADVISOR_DEFINITION_S3_BUCKET=my-cfn-artifacts-bucket \
TRUSTED_ADVISOR_SLACK_CHANNEL_ARN=arn:aws:chatbot:us-east-1:123456789012:chat-configuration/slack-channel/my-channel \
TRUSTED_ADVISOR_NOTIFICATION_REGIONS=us-east-1,ap-northeast-1,eu-west-1 \
TRUSTED_ADVISOR_REFRESH_SCHEDULE='rate(6 hours)' \
./deploy.sh deploy-stack
```

### 2. AWS CLIを使用したデプロイ（単一アカウント）

```bash
aws cloudformation deploy \
  --template-file cfn/stackset-template.yaml \
  --stack-name service-quota-monitoring \
  --parameter-overrides \
    TrustedAdvisorCheckIds=eW7HH0l7J9,c1z7kmr03n \
    TrustedAdvisorDefinitionS3Bucket=my-cfn-artifacts-bucket \
    TrustedAdvisorDefinitionS3Key=state-machines/service-quota-monitoring/trusted-advisor-refresh.asl.json \
    TrustedAdvisorSlackChannelArn=arn:aws:chatbot:us-east-1:123456789012:chat-configuration/slack-channel/my-channel \
    TrustedAdvisorNotificationRegions=us-east-1,ap-northeast-1,eu-west-1 \
    TrustedAdvisorRefreshSchedule='rate(6 hours)' \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

補足:
- scripts/deploy.sh は TRUSTED_ADVISOR_CHECK_IDS が指定されると、asl/trusted-advisor-refresh.asl.json をS3へアップロードしてからデプロイします。
- 既定のS3キーは state-machines/<STACK_NAME>/trusted-advisor-refresh.asl.json です。
- Regions は TrustedAdvisorNotificationRegions で調整できます。主要リージョンが既定値として設定されています。
- Trusted Advisorイベント起点のため、us-east-1 は対象リージョンに必ず含めてください。
- SNSおよびCloudWatchアラームは作成しません。

### 3. StackSetとしてデプロイ（複数アカウント）

```bash
cd scripts

# StackSet を作成
./deploy.sh deploy-stackset

# 組織OUに対してStackSetインスタンスを追加
OU_IDS=ou-xxxx-xxxxxxxx REGIONS=ap-northeast-1,us-east-1 ./deploy.sh add-instances

# 特定のアカウントに追加
ACCOUNT_IDS=123456789012,234567890123 REGIONS=ap-northeast-1 ./deploy.sh add-instances
```

## Trusted AdvisorチェックIDの調べ方

```bash
aws support describe-trusted-advisor-checks \
  --language en \
  --region us-east-1
```

必要なチェックの id を抜き出し、TrustedAdvisorCheckIds にカンマ区切りで設定してください。

## ステータス確認

```bash
# スタックのステータス確認
./scripts/deploy.sh status

# Step Functions（us-east-1）
aws stepfunctions list-state-machines --region us-east-1

# AWS User Notifications 設定確認
aws notifications list-notification-configurations --region us-east-1
```

## ステートマシン単体テスト（TestState API + Step Functions Local）

このディレクトリの `asl/trusted-advisor-refresh.asl.json` は次の2段階でテストするのが実運用向きです。

- TestState API: ステート単位（主にデータ変換・分岐）
- Step Functions Local: ステートマシン全体の遷移（ローカル実行）

### 1. TestState API でステート単位を検証

`PrepareCheckIdList` は `States.StringSplit` の変換ロジックのみなので、TestState API で高速に検証できます。

```bash
aws stepfunctions test-state \
  --region us-east-1 \
  --definition '{
    "Type": "Pass",
    "Parameters": {
      "checkIdList.$": "States.StringSplit($.checkIds, \",\")"
    },
    "ResultPath": "$.work",
    "End": true
  }' \
  --input '{"checkIds":"eW7HH0l7J9,c1z7kmr03n"}'
```

期待値（抜粋）:

```json
{
  "checkIds": "eW7HH0l7J9,c1z7kmr03n",
  "work": {
    "checkIdList": [
      "eW7HH0l7J9",
      "c1z7kmr03n"
    ]
  }
}
```

補足:
- `RefreshCheck` は `arn:aws:states:::aws-sdk:support:refreshTrustedAdvisorCheck` を呼ぶ `Task` のため、TestState API 単体では外部依存の影響を受けます。
- そのため `Task` を含む挙動（Map/Catch/End）は Step Functions Local 側で確認するのがおすすめです。

### 2. Step Functions Local でワークフロー全体を検証

Docker で Step Functions Local を起動します。

```bash
docker run --rm -p 8083:8083 amazon/aws-stepfunctions-local
```

別ターミナルでローカルエンドポイントを指定してステートマシンを作成・実行します。

```bash
# ローカル用のダミーIAMロールARNで作成（Local実行では実在不要）
aws stepfunctions create-state-machine \
  --endpoint-url http://localhost:8083 \
  --name ta-refresh-local \
  --definition file://asl/trusted-advisor-refresh.asl.json \
  --role-arn arn:aws:iam::012345678901:role/DummyRole

aws stepfunctions start-execution \
  --endpoint-url http://localhost:8083 \
  --state-machine-arn arn:aws:states:us-east-1:012345678901:stateMachine:ta-refresh-local \
  --input '{"checkIds":"eW7HH0l7J9,c1z7kmr03n"}'
```

確認コマンド:

```bash
aws stepfunctions list-executions \
  --endpoint-url http://localhost:8083 \
  --state-machine-arn arn:aws:states:us-east-1:012345678901:stateMachine:ta-refresh-local

aws stepfunctions get-execution-history \
  --endpoint-url http://localhost:8083 \
  --execution-arn <execution-arn>
```

補足:
- `support:refreshTrustedAdvisorCheck` 呼び出し結果を安定化させたい場合は、Step Functions Local のモック機能（Mocked service integrations）を使って成功系/失敗系を固定化してください。
- 失敗系の単体テストは `RefreshCheck` の `Catch` が `IgnoreRefreshError` に遷移することを確認すると有効です。

### 3. 追加すると運用しやすいファイル

READMEだけでも手動テストは可能ですが、再現性を上げるなら次のファイル追加を推奨します。

- `tests/fixtures/trusted-advisor-refresh-input.json`
  - テスト入力（checkIds）を固定化
- `tests/fixtures/trusted-advisor-refresh-expected.json`
  - TestState API の期待値スナップショット
- `tests/stepfunctions/run-local-tests.sh`
  - Local起動済み前提で create/start/history を自動実行
- `tests/stepfunctions/MockConfigFile.json`
  - Step Functions Local のモック定義（成功系/失敗系）

上記を用意すると、CIで `TestState API（高速）` と `Step Functions Local（遷移確認）` を分離実行しやすくなります。

## クリーンアップ

```bash
# スタックを削除
./scripts/deploy.sh delete-stack

# StackSetを削除（先にインスタンスを削除する必要があります）
./scripts/deploy.sh delete-stackset
```

## 参考資料

- AWS Trusted Advisor
  - https://docs.aws.amazon.com/awssupport/latest/user/trusted-advisor.html
- Monitoring AWS Trusted Advisor check results with Amazon EventBridge
  - https://docs.aws.amazon.com/awssupport/latest/user/cloudwatch-events-ta.html
- AWS Trusted Advisor events (EventBridge)
  - https://docs.aws.amazon.com/eventbridge/latest/ref/events-ref-trustedadvisor.html
- AWS User Notifications
  - https://docs.aws.amazon.com/notifications/latest/userguide/what-is-service.html
- CloudFormation StackSets ドキュメント
  - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/what-is-cfnstacksets.html
