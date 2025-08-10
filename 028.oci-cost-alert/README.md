# OCI コストアラート

このTerraformコードは、Oracle Cloud Infrastructure (OCI) で予算アラート機能を実装します。指定した予算額を超えた場合に、指定したメールアドレスに通知を送信します。

## 概要

このモジュールは以下のリソースを作成します：

- **予算 (Budget)**: 指定した金額と期間での予算設定
- **予算アラートルール (Budget Alert Rule)**: 予算の閾値を超えた際のアラート設定
- **通知トピック (Notification Topic)**: アラート通知用のトピック
- **メール購読 (Email Subscription)**: 指定したメールアドレスへの通知設定

## 技術仕様

- **リージョン**: ap-osaka-1
- **Terraformバージョン**: >= 1.9.6
- **OCIプロバイダーバージョン**: ~> 6.0

## 必要なリソース

### 予算アラート・ルール
- 予算の設定（金額、期間）
- アラート閾値の設定（パーセンテージ）
- 通知先メールアドレスの設定

## ファイル構成

```
028.oci-cost-alert/
├── README.md                    # このファイル
├── terraform.tf                 # Terraformプロバイダー設定
├── variables.tf                 # 変数定義
├── budget.tf                    # 予算とアラートルールの設定
├── notification.tf              # 通知トピックとメール購読の設定
├── outputs.tf                   # 出力値の定義
└── terraform.tfvars.example     # 設定例ファイル
```

## 使用方法

### 1. 前提条件

- OCI CLIが設定済みであること
- 適切なOCIの認証情報が設定されていること
- 予算を作成するコンパートメントのOCIDが分かっていること

### 2. 設定ファイルの準備

`terraform.tfvars.example`をコピーして`terraform.tfvars`を作成し、必要な値を設定してください：

```hcl
# 必須: コンパートメントのOCID
compartment_id = "ocid1.compartment.oc1..your-compartment-ocid"

# 予算設定
budget_amount = 100
budget_reset_period = "MONTHLY"
budget_display_name = "月次予算アラート"

# アラート設定
alert_threshold_percentage = 80
alert_email_addresses = [
  "admin@example.com",
  "finance@example.com"
]
```

### 3. デプロイ

```bash
# 初期化
terraform init

# プランの確認
terraform plan

# 適用
terraform apply
```

### 4. 確認

デプロイ後、以下を確認してください：

1. OCIコンソールで予算が作成されていることを確認
2. 指定したメールアドレスに購読確認メールが届くので、確認リンクをクリック
3. アラートルールが正しく設定されていることを確認

## 設定パラメータ

### 必須パラメータ

| パラメータ名 | 説明 | 例 |
|-------------|------|-----|
| `compartment_id` | リソースを作成するコンパートメントのOCID | `ocid1.compartment.oc1..example` |
| `alert_email_addresses` | アラート通知先メールアドレスのリスト | `["admin@example.com"]` |

### オプションパラメータ

| パラメータ名 | デフォルト値 | 説明 |
|-------------|-------------|------|
| `region` | `ap-osaka-1` | OCIリージョン |
| `budget_amount` | `100` | 予算金額 |
| `budget_reset_period` | `MONTHLY` | 予算リセット期間 (MONTHLY/QUARTERLY/ANNUALLY) |
| `alert_threshold_percentage` | `80` | アラート発砲閾値（パーセンテージ） |
| `budget_display_name` | `Monthly Budget Alert` | 予算の表示名 |
| `notification_topic_name` | `budget-alert-topic` | 通知トピック名 |

## セキュリティ要件

- コンパートメントレベルでの適切なIAM権限が必要
- 予算管理権限（`manage budgets`）が必要
- 通知サービス権限（`manage ons-topics`, `manage ons-subscriptions`）が必要

## ネットワーク要件

- 特別なネットワーク設定は不要
- メール通知はOCIの通知サービスを使用

## その他の制約

- 予算は作成後に削除する際、関連するアラートルールも自動的に削除されます
- メール購読は手動で確認が必要です（確認メールのリンクをクリック）
- 予算の通貨は、テナンシーの通貨設定に依存します

## 出力値

デプロイ完了後、以下の情報が出力されます：

- `budget_id`: 作成された予算のOCID
- `alert_rule_id`: アラートルールのOCID
- `notification_topic_id`: 通知トピックのOCID
- `email_subscription_ids`: メール購読のOCIDリスト

## トラブルシューティング

### よくある問題

1. **権限エラー**: 適切なIAM権限が設定されているか確認してください
2. **メール通知が届かない**: 購読確認メールを確認し、確認リンクをクリックしてください
3. **予算が作成されない**: コンパートメントのOCIDが正しいか確認してください

### ログの確認

```bash
# Terraformの詳細ログを有効にする
export TF_LOG=DEBUG
terraform apply
```

## 参考資料

- [OCI Budget Service Documentation](https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/budgetsoverview.htm)
- [OCI Notification Service Documentation](https://docs.oracle.com/en-us/iaas/Content/Notification/Concepts/notificationoverview.htm)
- [OCI Terraform Provider Documentation](https://registry.terraform.io/providers/oracle/oci/latest/docs)