# CloudWatch Service Quota Monitoring StackSet

AWSサービスクォータの使用状況を監視するCloudWatchアラームを、CloudFormation StackSetとして複数のアカウント・リージョンにデプロイします。

## 概要

このCloudFormationテンプレートは以下のリソースを作成します：

- **Lambda関数**: スケジュール実行されてサービスクォータの使用状況を収集し、CloudWatchカスタムメトリクスとして発行します
- **EventBridgeルール**: Lambdaを定期実行するためのスケジュールルール
- **CloudWatchアラーム**: 各クォータの使用率がしきい値を超えた際にアラームを発火させます
- **SNSトピック**: アラーム通知先（既存トピックを指定することも可能）

## 監視対象のサービスクォータ

| サービス | クォータ | クォータコード | デフォルト上限 | メトリクスソース |
|---------|---------|------------|-------------|--------------|
| VPC | VPCs per Region | L-F678F1CE | 5 | Lambda カスタムメトリクス |
| EC2 | EC2-VPC Elastic IPs | L-0263D0A3 | 5 | Lambda カスタムメトリクス |
| RDS | DB instances | L-7B6409FD | 40 | Lambda カスタムメトリクス |
| EC2 | On-Demand Standard vCPU | L-1216C47A | 32 | AWS/Usage ネイティブメトリクス |
| Lambda | Concurrent Executions | L-B99A9384 | 1000 | AWS/Lambda ネイティブメトリクス |

## 前提条件

- AWS CLIがインストールされていること
- 適切なIAM権限があること
  - `cloudformation:*`
  - `lambda:*`
  - `events:*`
  - `iam:*`
  - `sns:*`
  - `cloudwatch:*`
- StackSetとして使用する場合：
  - AWS Organizationsが有効化されていること、または管理アカウントでのStackSet権限があること

## パラメータ

| パラメータ | 説明 | デフォルト値 |
|----------|------|------------|
| `ThresholdPercent` | アラームを発火するクォータ使用率（%） | 80 |
| `MonitoringSchedule` | Lambda実行スケジュール | rate(1 hour) |
| `NotificationEmail` | 通知先メールアドレス（任意） | (空) |
| `ExistingTopicArn` | 既存SNSトピックARN（任意） | (空) |
| `EC2StandardVCPUQuota` | EC2 On-Demand 標準vCPUクォータ上限 | 32 |
| `LambdaConcurrentExecutionsQuota` | Lambda同時実行数クォータ上限 | 1000 |

## デプロイ方法

### 1. スクリプトを使用したデプロイ（単一アカウント）

```bash
cd scripts

# 基本的なデプロイ（メール通知あり）
NOTIFICATION_EMAIL=admin@example.com ./deploy.sh deploy-stack

# デプロイ後に Lambda コードを上書き
./deploy.sh update-lambda-code

# しきい値を変更してデプロイ
THRESHOLD_PERCENT=70 NOTIFICATION_EMAIL=admin@example.com ./deploy.sh deploy-stack

# スケジュールを変更してデプロイ（5分ごと）
MONITORING_SCHEDULE="rate(5 minutes)" ./deploy.sh deploy-stack

# デプロイとコード上書きを連続実行
./deploy.sh deploy-and-update
```

### 2. AWS CLIを使用したデプロイ（単一アカウント）

```bash
aws cloudformation deploy \
  --template-file cfn/stackset-template.yaml \
  --stack-name service-quota-monitoring \
  --parameter-overrides \
    ThresholdPercent=80 \
    NotificationEmail=admin@example.com \
    EC2StandardVCPUQuota=32 \
    LambdaConcurrentExecutionsQuota=1000 \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --region ap-northeast-1
```

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

### 4. GitHub Actionsを使用したデプロイ

リポジトリの「Actions」タブから `CloudFormation Service Quota Monitoring Deploy` ワークフローを実行します。

必要な入力値：
- `issue_number`: デプロイ結果をコメントするIssue番号
- `deploy_type`: `stack`（単一アカウント）または `stackset`（複数アカウント）
- `region`: デプロイ先リージョン
- `threshold_percent`: アラームしきい値（%）
- `notification_email`: 通知先メールアドレス（任意）
- `stack_name`: スタック/StackSet名
- `ou_ids`: StackSetのデプロイ対象OU ID（StackSetの場合）
- `account_ids`: StackSetのデプロイ対象アカウントID（StackSetの場合）
- `regions`: StackSetインスタンスを作成するリージョン（StackSetの場合）

## ステータス確認

```bash
# スタックのステータス確認
./scripts/deploy.sh status

# CloudWatchアラームの確認
aws cloudwatch describe-alarms \
  --alarm-name-prefix service-quota-monitoring \
  --region ap-northeast-1
```

## クリーンアップ

```bash
# スタックを削除
./scripts/deploy.sh delete-stack

# StackSetを削除（先にインスタンスを削除する必要があります）
./scripts/deploy.sh delete-stackset
```

## カスタマイズ

### 監視するクォータの追加

`scripts/quota_monitor.py` の `QUOTAS` リストに追加します：

```python
QUOTAS = [
    # 既存のエントリ...
    {
        'service_code': 'ecs',  # サービスコード（aws service-quotas list-services で確認）
        'quota_code': 'L-xxxxxx',  # クォータコード
        'quota_name': 'ECS Clusters',
        'resource_type': 'ecs-clusters',  # カスタム処理が必要
    },
]
```

対応するリソース数取得ロジックを `get_resource_count` 関数に追加します。

## Lambdaコードの配置

このテンプレートでは Lambda の Python コード本体を CloudFormation テンプレートへ埋め込まず、テンプレートデプロイ時はプレースホルダーコードで関数を作成します。その後、`scripts/deploy.sh update-lambda-code` により `aws lambda update-function-code` を使って `scripts/quota_monitor.py` を直接反映します。

必須環境変数:

- なし

任意環境変数:

- `LAMBDA_SOURCE_FILE`: Lambda ソースファイル（デフォルト: `scripts/quota_monitor.py`）

### クォータコードの確認方法

```bash
# サービス一覧の確認
aws service-quotas list-services --region ap-northeast-1

# 特定サービスのクォータ一覧
aws service-quotas list-service-quotas \
  --service-code vpc \
  --region ap-northeast-1

# 特定クォータの現在値確認
aws service-quotas get-service-quota \
  --service-code vpc \
  --quota-code L-F678F1CE \
  --region ap-northeast-1
```

## 参考資料

- [AWS Service Quotas ドキュメント](https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html)
- [CloudWatch Metrics Math](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/using-metric-math.html)
- [CloudFormation StackSets ドキュメント](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/what-is-cfnstacksets.html)
- [AWS/Usage CloudWatch Metrics](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring_ec2.html)
