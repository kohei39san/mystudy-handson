# OCI コストアラート設定

このTerraformコードは、Oracle Cloud Infrastructure (OCI) でコストアラート機能を実装します。指定した予算額を超えた場合に、指定のメールアドレスに通知を送信します。

## 概要

このソリューションは以下のOCIリソースを作成します：

- **予算 (Budget)**: 月次予算の設定
- **予算アラートルール (Budget Alert Rules)**: 複数の閾値でのアラート設定
- **通知トピック (ONS Topic)**: アラート通知の配信
- **メール購読 (Email Subscription)**: 指定メールアドレスへの通知配信

## アーキテクチャ

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     予算        │───▶│ アラートルール    │───▶│  通知トピック   │
│   (Budget)      │    │ (Alert Rules)    │    │  (ONS Topic)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │  メール通知     │
                                                │ (Email Alert)   │
                                                └─────────────────┘
```

## 機能

### アラートルール

1. **カスタム閾値アラート**: 設定した割合（デフォルト80%）で通知
2. **100%アラート**: 予算の100%に達した時点で通知
3. **予測アラート**: 月末までに予算を超過する予測の場合に通知

### 通知内容

- 現在の使用率
- 予算金額と通貨
- アラートの種類（実際の使用量 or 予測）

## 前提条件

- OCI CLI または適切な認証情報の設定
- 適切な権限を持つOCIユーザー
- 有効なコンパートメントOCID
- 通知を受信するメールアドレス

## 必要な権限

以下のOCI権限が必要です：

```
Allow group <group-name> to manage budgets in compartment <compartment-name>
Allow group <group-name> to manage ons-topics in compartment <compartment-name>
Allow group <group-name> to manage ons-subscriptions in compartment <compartment-name>
```

## 使用方法

### 1. 設定ファイルの準備

```bash
# サンプル設定ファイルをコピー
cp terraform.tfvars.example terraform.tfvars

# 設定ファイルを編集
vi terraform.tfvars
```

### 2. 必須変数の設定

`terraform.tfvars`ファイルで以下の値を設定してください：

```hcl
# 必須項目
compartment_id = "ocid1.compartment.oc1..your-compartment-ocid"
alert_email    = "your-email@example.com"

# オプション項目（必要に応じて変更）
budget_amount              = 100
budget_currency            = "USD"
alert_threshold_percentage = 80
budget_display_name        = "Monthly Budget Alert"
```

### 3. Terraformの実行

```bash
# 初期化
terraform init

# プランの確認
terraform plan

# リソースの作成
terraform apply
```

### 4. メール購読の確認

リソース作成後、指定したメールアドレスに購読確認メールが送信されます。メール内のリンクをクリックして購読を確認してください。

## 設定可能な変数

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `compartment_id` | コンパートメントOCID | - | ✓ |
| `alert_email` | アラート通知先メールアドレス | - | ✓ |
| `region` | OCIリージョン | `ap-osaka-1` | - |
| `budget_amount` | 予算金額 | `100` | - |
| `budget_currency` | 予算通貨 | `USD` | - |
| `alert_threshold_percentage` | アラート閾値（%） | `80` | - |
| `budget_display_name` | 予算の表示名 | `Monthly Budget Alert` | - |
| `notification_topic_name` | 通知トピック名 | `budget-alert-topic` | - |
| `freeform_tags` | フリーフォームタグ | 基本タグセット | - |

## 出力値

| 出力名 | 説明 |
|--------|------|
| `budget_id` | 作成された予算のOCID |
| `notification_topic_id` | 通知トピックのOCID |
| `email_subscription_id` | メール購読のOCID |
| `alert_rules` | 作成されたアラートルールの詳細情報 |

## 注意事項

### セキュリティ

- メールアドレスは機密情報として扱われ、出力時にマスクされます
- 適切なIAMポリシーを設定して、必要最小限の権限のみを付与してください

### コスト

- ONS（Oracle Notification Service）の使用料金が発生する場合があります
- 予算アラート機能自体は無料ですが、通知の配信に少額の料金が発生する可能性があります

### 制限事項

- 予算は月次リセットのみサポート
- アラート閾値は1-100%の範囲で設定
- メール通知のみサポート（SMS、Slack等は別途設定が必要）

## トラブルシューティング

### よくある問題

1. **メール通知が届かない**
   - 購読確認メールを確認してください
   - スパムフォルダを確認してください
   - メールアドレスが正しく設定されているか確認してください

2. **権限エラー**
   - 必要なIAMポリシーが設定されているか確認してください
   - コンパートメントOCIDが正しいか確認してください

3. **予算が作成されない**
   - コンパートメントIDが有効か確認してください
   - 予算金額が正の数値か確認してください

## リソースの削除

```bash
# 全リソースの削除
terraform destroy
```

**注意**: リソースを削除すると、設定されたアラートも無効になります。

## サポート

このコードに関する質問や問題がある場合は、以下を確認してください：

1. [OCI公式ドキュメント](https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/budgetsoverview.htm)
2. [Terraform OCI Provider ドキュメント](https://registry.terraform.io/providers/oracle/oci/latest/docs)

## ライセンス

このコードはMITライセンスの下で提供されています。