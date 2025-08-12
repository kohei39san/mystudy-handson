# 027.oci-cost-alert - OCIコストアラート

## 概要

このTerraformコードは、Oracle Cloud Infrastructure (OCI) でコストアラート機能を実装します。指定した予算額を超えた場合に、指定のメールアドレスに通知を送信する仕組みを構築します。

## 機能

- **予算管理**: 月次予算の設定と管理
- **アラート通知**: 予算の閾値に達した際のメール通知
- **複数段階アラート**: 
  - 設定可能な閾値（デフォルト80%）でのアラート
  - 100%到達時のアラート
  - 予算超過予測アラート

## 構成リソース

### 主要リソース

1. **oci_budget_budget**: 月次予算の定義
2. **oci_budget_alert_rule**: 予算アラートルールの設定
3. **oci_ons_notification_topic**: 通知トピック
4. **oci_ons_subscription**: メール通知の購読設定

### リソース詳細

- **予算**: 月次リセットの予算設定
- **通知トピック**: アラート通知用のONS（Oracle Notification Service）トピック
- **メール購読**: 指定されたメールアドレスへの通知設定
- **アラートルール**: 
  - 閾値アラート（デフォルト80%）
  - 100%到達アラート
  - 予算超過予測アラート

## 使用方法

### 1. 前提条件

- OCI CLIまたはTerraform用のOCI認証情報が設定済みであること
- 適切なIAMポリシーが設定されていること（Budget、ONS関連の権限）

### 2. 設定ファイルの準備

```bash
# terraform.tfvars.exampleをコピーして設定
cp terraform.tfvars.example terraform.tfvars
```

### 3. 必須変数の設定

`terraform.tfvars`ファイルで以下の変数を設定してください：

```hcl
compartment_id = "ocid1.compartment.oc1..aaaaaaaa..."  # コンパートメントOCID
alert_email    = "your-email@example.com"              # アラート受信メールアドレス
```

### 4. デプロイ

```bash
# Terraformの初期化
terraform init

# 実行計画の確認
terraform plan

# リソースの作成
terraform apply
```

## 設定可能な変数

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `region` | OCIリージョン | `ap-osaka-1` | No |
| `compartment_id` | コンパートメントOCID | - | Yes |
| `budget_amount` | 予算額 | `100` | No |
| `budget_currency` | 通貨 | `USD` | No |
| `alert_email` | アラート受信メールアドレス | - | Yes |
| `alert_threshold_percentage` | アラート閾値（%） | `80` | No |
| `budget_display_name` | 予算の表示名 | `Monthly Budget Alert` | No |
| `notification_topic_name` | 通知トピック名 | `budget-alert-topic` | No |
| `freeform_tags` | フリーフォームタグ | `{Environment = "production", Terraform = "true"}` | No |

## 出力値

- `budget_id`: 作成された予算のOCID
- `budget_display_name`: 予算の表示名
- `notification_topic_id`: 通知トピックのOCID
- `notification_topic_name`: 通知トピック名
- `email_subscription_id`: メール購読のOCID
- `alert_rules`: 作成されたアラートルールの情報

## セキュリティ考慮事項

- コンパートメントレベルでの予算管理により、適切なスコープでのコスト監視を実現
- ONSを使用した安全なメール通知
- フリーフォームタグによるリソース管理

## 注意事項

1. **メール確認**: 初回デプロイ後、指定したメールアドレスに確認メールが送信されます。購読を有効にするために確認が必要です。

2. **権限要件**: 以下のOCI IAMポリシーが必要です：
   ```
   Allow group <group-name> to manage budgets in compartment <compartment-name>
   Allow group <group-name> to manage ons-topics in compartment <compartment-name>
   Allow group <group-name> to manage ons-subscriptions in compartment <compartment-name>
   ```

3. **通貨設定**: 予算の通貨は、OCIアカウントの請求通貨と一致させることを推奨します。

4. **アラート頻度**: アラートは条件を満たした際に送信されますが、スパム防止のため一定の間隔で制限される場合があります。

## トラブルシューティング

### よくある問題

1. **メール通知が届かない**
   - メールアドレスの確認が完了しているか確認
   - スパムフォルダを確認
   - ONSサブスクリプションのステータスを確認

2. **権限エラー**
   - 必要なIAMポリシーが設定されているか確認
   - コンパートメントIDが正しいか確認

3. **予算が作成されない**
   - コンパートメントIDの形式が正しいか確認
   - 予算額と通貨の設定を確認

## 関連ドキュメント

- [OCI Budget Service Documentation](https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/budgetsoverview.htm)
- [OCI Notification Service Documentation](https://docs.oracle.com/en-us/iaas/Content/Notification/Concepts/notificationoverview.htm)
- [OCI Terraform Provider Documentation](https://registry.terraform.io/providers/oracle/oci/latest/docs)