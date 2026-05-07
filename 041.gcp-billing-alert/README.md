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
- Node.js v18 以上
- npm または yarn

## 前提条件

1. **Google Cloud APIの有効化**
   ```bash
   gcloud services enable config.googleapis.com
   gcloud services enable billingbudgets.googleapis.com
   gcloud services enable monitoring.googleapis.com
   ```

2. **必要な権限**
   - `roles/infra-manager.admin` - Infrastructure Manager 管理者
   - `roles/billing.budgetsBudgetOwner` - Billing Budgets オーナー

3. **Google Cloud認証**
   
   オプション1: gcloud CLIで認証
   ```bash
   gcloud auth application-default login
   ```

   オプション2: Service Account キーを使用
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

## ファイル構成

```
041.gcp-billing-alert/
├── README.md                    # このファイル
├── terraform.tf                 # Terraformプロバイダー設定
├── variables.tf                 # 変数定義
├── budget.tf                    # 予算と通知チャンネルの設定
├── outputs.tf                   # 出力値の定義
├── terraform.tfvars.example     # 設定例ファイル
├── deploy.ts                    # Infrastructure Manager API実行スクリプト
├── package.json                 # npm設定
├── tsconfig.json                # TypeScript設定
└── .env.example                 # 環境変数テンプレート
```

## 使用方法

### 1. 環境セットアップ

```bash
# パッケージをインストール
npm install
```

### 2. 設定ファイルの準備

```bash
# 環境変数ファイルを作成
cp .env.example .env

# .env ファイルを編集して以下の値を設定
# - GCP_PROJECT_ID: あなたのプロジェクトID
# - GCP_LOCATION: デプロイメント場所（例：us-central1）
# - DEPLOYMENT_NAME: デプロイメント名
```

```bash
# terraform.tfvars を作成
cp terraform.tfvars.example terraform.tfvars

# terraform.tfvars を編集して以下の値を設定
# - project_id: Google Cloud プロジェクトID（必須）
# - billing_account_id: 請求先アカウントID（必須）
# - alert_email_addresses: アラート通知先メールアドレス（必須）
```

### 3. デプロイメント実行

Infrastructure Manager にTerraformをデプロイします：

```bash
# デプロイ実行
npm run deploy
```

**実行時の処理:**
1. Terraformファイルを読み込み
2. Infrastructure Manager にデプロイメントを作成
3. 予算（Budget）と通知チャネル（Notification Channel）を作成

**期待される出力:**
```
🌍 Google Cloud Infrastructure Manager にデプロイ中...

📂 Terraformファイルを読み込み中...
  ✓ terraform.tf
  ✓ variables.tf
  ✓ budget.tf
  ✓ outputs.tf

📝 デプロイメントを作成中...
✓ デプロイメント作成リクエストが送信されました

🚀 デプロイメントを適用中...
✓ デプロイメントが適用されました
  状態: APPLIED

✅ デプロイが完了しました！
```

### 4. デプロイメント状態の確認

```bash
npm run status
```

**出力例:**
```
📊 デプロイメント状態:
  名前: projects/YOUR_PROJECT/locations/us-central1/deployments/gcp-billing-alert-deployment
  状態: APPLIED
  作成日: 2024-05-08T10:30:00Z
  更新日: 2024-05-08T10:35:00Z
```

### 5. リソース削除

不要になった場合はリソースを削除します：

```bash
npm run destroy
```

**注意:** このコマンドはすべての関連リソース（予算、モニタリングチャネル）も削除します。

## トラブルシューティング

### エラー: "Permission denied"

**解決方法:**
```bash
# 認証を再設定
gcloud auth application-default login
```

### エラー: "The caller does not have permission"

**必要な権限を確認・追加:**
```bash
# サービスアカウントに権限を付与
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:SA_EMAIL \
  --role=roles/infra-manager.admin

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:SA_EMAIL \
  --role=roles/billing.budgetsBudgetOwner
```

### エラー: API not enabled

**必要なAPIを有効化:**
```bash
gcloud services enable config.googleapis.com
gcloud services enable billingbudgets.googleapis.com
gcloud services enable monitoring.googleapis.com
```

## Google Cloud Consoleでの確認

デプロイ後、以下のリンクで確認できます：

1. **Infrastructure Manager ダッシュボード**
   - https://console.cloud.google.com/infra-manager/deployments

2. **予算設定**
   - https://console.cloud.google.com/billing/budgets

3. **モニタリング チャネル**
   - https://console.cloud.google.com/monitoring/alerting/notificationchannels

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

- [Infrastructure Manager API リファレンス](https://cloud.google.com/docs/config/api)
- [Google Cloud Node.js クライアントライブラリ](https://cloud.google.com/nodejs/docs)
- [Google Cloud Billing Budgets](https://cloud.google.com/billing/docs/how-to/budgets)
- [Terraform google_billing_budget](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/billing_budget)
- [Terraform google_monitoring_notification_channel](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/monitoring_notification_channel)
