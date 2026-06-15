# Google Cloud 課金アラート

このTerraformコードは、Google Cloud で課金アラート機能を実装します。指定した予算額の閾値を超えた場合に、指定したメールアドレスに通知を送信します。

## 概要

![Architecture Diagram](src/architecture.svg)

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
- 事前作成済み Cloud Storage バケット（Terraformソース配置用）

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

このセクションでは、デプロイまでの全ステップを順番に説明します。

### ステップ 1: 前提条件の確認・準備

#### 1.1 Google Cloud APIの有効化

下記の 3 つの API を有効化してください：

```bash
gcloud services enable config.googleapis.com
gcloud services enable billingbudgets.googleapis.com
gcloud services enable monitoring.googleapis.com
```

#### 1.2 Google Cloud 認証

次のいずれかの方法で認証を設定してください：

**方法 1: gcloud CLI で認証（推奨）**
```bash
gcloud auth application-default login
```

**方法 2: Service Account キーを使用**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

#### 1.3 Cloud Storage バケットの作成

Terraform のソースコードを保存するバケットを作成します：

```bash
gsutil mb gs://your-billing-alert-bucket
```

### ステップ 2: ローカル環境のセットアップ

```bash
# リポジトリディレクトリに移動
cd 041.gcp-billing-alert

# npm 依存パッケージのインストール
npm install

# 環境変数ファイルのコピー
cp .env.example .env
```

### ステップ 3: .env ファイルの設定

エディタで `.env` を開き、必須項目を設定します。

#### 必須項目（全ユーザー共通）

```bash
# Google Cloud プロジェクト・インフラストラクチャ設定
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=asia-northeast1
DEPLOYMENT_NAME=billing-alert-deployment
GCP_SERVICE_ACCOUNT=infra-manager-runner@your-project-id.iam.gserviceaccount.com

# Terraform 変数
TF_PROJECT_ID=your-project-id
TF_BILLING_ACCOUNT_ID=your-billing-account-id
TF_ALERT_EMAIL_ADDRESSES=["admin@example.com","finance@example.com"]
```

Infrastructure Manager が Terraform ソース ZIP を読むため、`GCP_SERVICE_ACCOUNT` には少なくともソースバケットに対する権限を付与してください。`roles/storage.objectViewer` に加えて、バケットの存在確認で `roles/storage.bucketViewer` が必要になることがあります。対象は `GCS_SOURCE_URI` のバケットです。

#### オプション項目（必要に応じて設定）

```bash
# 予算設定
TF_BUDGET_AMOUNT=1000           # 予算金額（デフォルト: 1）
TF_CURRENCY_CODE=JPY            # 通貨コード（デフォルト: JPY）
TF_BUDGET_DISPLAY_NAME=Monthly-Billing-Alert  # 予算名

# アラート設定
TF_ALERT_THRESHOLD_PERCENTAGES=[50,80,100]  # アラート閾値（%）
TF_REGION=asia-northeast1       # リージョン
```

### ステップ 4: デプロイメント実行（2つの方法から選択）

#### **パス A: 自動アップロード（推奨）**

`deploy.ts` が Terraform ファイルの zip 作成と GCS アップロードを自動で実行します。

**設定:**
```bash
AUTO_UPLOAD_TERRAFORM=true
ARTIFACTS_GCS_BUCKET=your-billing-alert-bucket
TF_DIR=./
```

**実行:**
```bash
npm run deploy
```

このコマンドで以下が自動実行されます：
1. Terraform ファイル（.tf）を zip 化
2. GCS バケットにアップロード
3. Infrastructure Manager デプロイメント作成

#### **パス B: 手動アップロード**

Terraform ファイルを自分で zip 化して GCS にアップロードする場合：

**設定:**
```bash
AUTO_UPLOAD_TERRAFORM=false
GCS_SOURCE_URI=gs://your-billing-alert-bucket/terraform.zip
```

`GCS_SOURCE_URI` は `gs://` から始まる ZIP の完全なパスを指定します。`GCP_SERVICE_ACCOUNT` には、このバケットを読み取れる権限を付与してください。

**実行:**
```bash
# Terraform ファイルを zip 化
zip -r terraform.zip terraform.tf variables.tf budget.tf outputs.tf

# GCS にアップロード
gsutil cp terraform.zip gs://your-billing-alert-bucket/terraform.zip

# デプロイメント作成
npm run deploy
```

### ステップ 5: デプロイメントの状態確認

```bash
# デプロイメント状態を確認
npm run status
```

Google Cloud Console でも確認できます：
- **Infrastructure Manager**: https://console.cloud.google.com/infra-manager/deployments
- **予算設定**: https://console.cloud.google.com/billing/budgets
- **通知チャネル**: https://console.cloud.google.com/monitoring/alerting/notificationchannels

### ステップ 6: クリーンアップ（不要な場合）

```bash
# デプロイメント削除
npm run destroy
```

`destroy` は Infrastructure Manager の `force=true` で削除します。

## `.env` の全設定項目リファレンス

| 環境変数 | 必須？ | デフォルト | 説明 | パス |
|---------|--------|----------|------|------|
| `GCP_PROJECT_ID` | ✓ | - | Google Cloud プロジェクト ID | A, B |
| `GCP_LOCATION` | ✓ | - | Infrastructure Manager デプロイメント場所 | A, B |
| `DEPLOYMENT_NAME` | ✓ | - | デプロイメント名 | A, B |
| `GCP_SERVICE_ACCOUNT` | ✓ | - | Infrastructure Manager 実行用サービスアカウント | A, B |
| `AUTO_UPLOAD_TERRAFORM` | ✗ | false | true で自動 zip/upload | A |
| `ARTIFACTS_GCS_BUCKET` | ✗ | - | Terraform zip 保存先バケット | A |
| `TF_DIR` | ✗ | ./ | Terraform ファイルディレクトリ | A |
| `GCS_SOURCE_URI` | ✗ | - | Terraform zip の GCS URI (gs://...) | B |
| `TF_PROJECT_ID` | ✓ | - | Terraform が使用する GCP プロジェクト ID | A, B |
| `TF_BILLING_ACCOUNT_ID` | ✓ | - | Terraform が使用する請求先アカウント ID | A, B |
| `TF_ALERT_EMAIL_ADDRESSES` | ✓ | - | アラート通知先メール（JSON 配列またはカンマ区切り） | A, B |
| `TF_BUDGET_AMOUNT` | ✗ | 1 | 予算金額 | A, B |
| `TF_CURRENCY_CODE` | ✗ | JPY | 通貨コード | A, B |
| `TF_BUDGET_DISPLAY_NAME` | ✗ | Monthly-Billing-Alert | 予算の表示名 | A, B |
| `TF_ALERT_THRESHOLD_PERCENTAGES` | ✗ | [50,80,100] | アラート閾値（%、JSON 配列） | A, B |
| `TF_REGION` | ✗ | asia-northeast1 | Google Cloud リージョン | A, B |

## バケット権限の確認

`Revision failed ... does not have access to the bucket` が出る場合は、`GCS_SOURCE_URI` のバケットに対して、`GCP_SERVICE_ACCOUNT` に以下を付与してください。

- `roles/storage.objectViewer`
- `roles/storage.bucketViewer`

必要なら、権限付与後に数分待ってから再実行してください。

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
