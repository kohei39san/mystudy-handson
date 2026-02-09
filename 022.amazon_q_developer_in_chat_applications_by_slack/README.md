# Amazon Q Developer in Chat Applications by Slack

![アーキテクチャ図](src/architecture.svg)

このTerraform構成は、SlackでAmazon Q Developerを使用するためのCloudFormationスタックをデプロイします。

## リソース構成

このTerraform構成では以下のリソースを作成します：

### CloudFormation Stack
- **スタック名**: amazon-q-developer-in-slack
- **テンプレート**: src/cfn/template.yaml
- **機能**: CAPABILITY_NAMED_IAM（IAMリソース作成権限）

### 必要なパラメータ
- **SlackWorkspaceId**: SlackワークスペースのID
- **SlackChannelId**: 対象SlackチャンネルのID
- **SlackChannelName**: 対象Slackチャンネルの名前

## ファイル構成

```
022.amazon_q_developer_in_chat_applications_by_slack/
├── main.tf                      # メインのTerraform設定
├── outputs.tf                   # 出力値の定義
├── terraform.tf                 # Terraformプロバイダー設定
├── variables.tf                 # 変数定義
├── terraform.tfvars.example     # 設定例ファイル
└── src/
    └── cfn/
        └── template.yaml        # CloudFormationテンプレート
```

## 使用方法

### 1. 前提条件

- AWS CLIが設定済みであること
- 適切なAWS認証情報が設定されていること
- SlackワークスペースとチャンネルのIDが分かっていること

### 2. 設定ファイルの準備

`terraform.tfvars.example`をコピーして`terraform.tfvars`を作成し、必要な値を設定してください：

```hcl
# Slack設定
slack_workspace_id = "T1234567890"
slack_channel_id   = "C1234567890"
slack_channel_name = "amazon-q-developer"

# 環境設定
environment = "production"
```

### 3. デプロイ

```bash
# 初期化
terraform init

# プランの確認
terraform plan

# 適用
terraform apply

# 削除
terraform destroy
```

## 注意事項

- SlackワークスペースとチャンネルのIDは事前に取得しておく必要があります
- Amazon Q Developerの利用には適切なAWSアカウントとサブスクリプションが必要です
- CloudFormationスタックはIAMリソースを作成するため、適切な権限が必要です

## セキュリティ要件

- IAMロール作成権限（`iam:CreateRole`, `iam:AttachRolePolicy`等）が必要
- CloudFormation実行権限が必要
- Amazon Q Developerサービスへのアクセス権限が必要
# Slackでやり取りできるAmazon Q Developer in chat applications（Chatbot）

## 概要

このプロジェクトは、SlackチャンネルでAmazon Q Developer（AWS Chatbot）を利用できるようにするためのTerraformおよびCloudFormationテンプレートを提供します。

## 構成

このプロジェクトでは以下のリソースを作成します：

1. **IAMロール (IAMR-amazon-q-developer-in-slack)**
   - Amazon Q Developer in chat applicationsに紐づけるチャネルIAMロール
   - `AWSResourceExplorerReadOnlyAccess` ポリシーがアタッチされています

2. **IAMポリシー (IAMP-amazon-q-developer-in-slack)**
   - IAMR-amazon-q-developer-in-slackに紐づけるIAMポリシー
   - CloudWatchに対する読み取り権限を持ちます

3. **AWS Chatbot Slack設定**
   - `AWS::Chatbot::SlackChannelConfiguration` リソースを使用
   - ガードレールポリシーとして `ReadOnlyAccess` と `AmazonQDeveloperAccess` を設定
   - `UserRoleRequired` は `false` に設定

## 使用方法

### 前提条件

1. AWS CLIがインストールされ、適切に設定されていること
2. Terraformがインストールされていること（バージョン1.0.0以上）
3. SlackワークスペースとチャンネルがAWS Chatbotと連携済みであること

### デプロイ手順

1. 必要に応じて変数を設定します：

```bash
# terraform.tfvarsファイルを作成
cat > terraform.tfvars << EOF
slack_workspace_id = "あなたのSlackワークスペースID"
slack_channel_id   = "あなたのSlackチャンネルID"
slack_channel_name = "あなたのSlackチャンネル名"
environment        = "prod"  # 必要に応じて変更
EOF
```

2. Terraformを初期化します：

```bash
terraform init
```

3. デプロイ計画を確認します：

```bash
terraform plan
```

4. リソースをデプロイします：

```bash
terraform apply
```

5. デプロイが完了すると、Slackチャンネルで Amazon Q Developer を利用できるようになります。

## 変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|------------|
| slack_workspace_id | SlackワークスペースのID | T0123456789 (ダミー値) |
| slack_channel_id | SlackチャンネルのID | C0123456789 (ダミー値) |
| slack_channel_name | Slackチャンネルの名前 | aws-chatbot (ダミー値) |
| environment | 環境名（タグ付け用） | dev |

## 出力値

| 出力名 | 説明 |
|--------|------|
| slack_channel_configuration_arn | Slack Channel ConfigurationのARN |
| iam_role_arn | Amazon Q Developer用IAMロールのARN |

## 注意事項

- このテンプレートを使用する前に、AWS ChatbotとSlackの連携が完了している必要があります。
- 必要に応じて、IAMポリシーのアクセス権限を調整してください。
- 本番環境で使用する場合は、セキュリティ要件に合わせて設定を見直してください。