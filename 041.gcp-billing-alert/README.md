# Google Cloud 課金アラート

このTerraformコードは、Google Cloud で課金アラート機能を実装します。指定した予算額の閾値を超えた場合に、指定したメールアドレスに通知を送信します。

## 概要

このモジュールは以下のリソースを作成します：

- **予算 (Billing Budget)**: 指定した金額と通貨での予算設定
- **通知チャンネル (Monitoring Notification Channel)**: アラート通知用のメールチャンネル

## 技術仕様

- **リージョン**: asia-northeast1
- **Terraformバージョン**: >= 1.9.6
- **Google Cloudプロバイダーバージョン**: ~> 6.0

## 必要なリソース

- Google Cloud プロジェクト
- Google Cloud 請求先アカウント
- Terraform実行環境

## ファイル構成

```
041.gcp-billing-alert/
├── README.md                    # このファイル
├── terraform.tf                 # Terraformプロバイダー設定
├── variables.tf                 # 変数定義
├── budget.tf                    # 予算と通知チャンネルの設定
├── outputs.tf                   # 出力値の定義
└── terraform.tfvars.example     # 設定例ファイル
```

## 使用方法

### 1. 前提条件

以下のAPIが有効になっていることを確認してください：

```bash
gcloud services enable billingbudgets.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### 2. 設定ファイルの準備

`terraform.tfvars.example`をコピーして`terraform.tfvars`を作成し、必要な値を設定してください：

```hcl
# 必須: Google Cloud プロジェクトID
project_id = "your-gcp-project-id"

# 必須: 請求先アカウントID
billing_account_id = "XXXXXX-XXXXXX-XXXXXX"

# 必須: アラート通知先メールアドレス
alert_email_addresses = [
  "admin@example.com",
  "finance@example.com"
]

# 予算設定
budget_amount = 1000
currency_code = "JPY"
budget_display_name = "Monthly Billing Alert"

# アラート閾値（%）
alert_threshold_percentages = [50, 80, 100]
```

### 3. Terraformの実行

```bash
# バックエンド設定（GCSバケット）
terraform init -backend-config="bucket=your-tfstate-bucket"

# 実行計画の確認
terraform plan

# リソースの作成
terraform apply
```

## 設定パラメータ

| パラメータ | 型 | デフォルト値 | 説明 |
|---|---|---|---|
| `project_id` | string | - | Google Cloud プロジェクトID（必須） |
| `billing_account_id` | string | - | 請求先アカウントID（必須） |
| `alert_email_addresses` | list(string) | - | アラート通知先メールアドレス（必須） |
| `budget_amount` | number | 1 | 予算金額 |
| `currency_code` | string | JPY | 通貨コード |
| `budget_display_name` | string | Monthly-Billing-Alert | 予算の表示名 |
| `alert_threshold_percentages` | list(number) | [50, 80, 100] | アラート閾値（%） |
| `region` | string | asia-northeast1 | Google Cloudリージョン |

## セキュリティ要件

Terraform実行ユーザーまたはサービスアカウントに以下の権限が必要です：

- `billing.budgets.create`
- `billing.budgets.update`
- `monitoring.notificationChannels.create`
- `monitoring.notificationChannels.update`

## 出力値

| 出力名 | 説明 |
|---|---|
| `budget_id` | 作成された予算のID |
| `budget_display_name` | 予算の表示名 |
| `budget_amount` | 予算金額 |
| `alert_threshold_percentages` | 設定されたアラート閾値（%） |
| `notification_channel_ids` | 通知チャンネルのID一覧 |
| `alert_email_addresses` | アラート通知先メールアドレス |

## 参考資料

- [Google Cloud Billing Budgets](https://cloud.google.com/billing/docs/how-to/budgets)
- [Terraform google_billing_budget](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/billing_budget)
- [Terraform google_monitoring_notification_channel](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/monitoring_notification_channel)
