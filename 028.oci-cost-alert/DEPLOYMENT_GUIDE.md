# OCI コストアラート デプロイメントガイド

このガイドでは、OCI（Oracle Cloud Infrastructure）でコストアラートを設定するためのTerraformコードのデプロイ方法を詳しく説明します。

## 前提条件

### 1. 必要なツール

- **Terraform**: バージョン 1.9.6 以上
- **OCI CLI**: 最新版（オプション、推奨）
- **Git**: リポジトリのクローン用

### 2. OCI アカウントと権限

以下の権限が必要です：

- `manage budgets` - 予算の作成・管理
- `manage ons-topics` - 通知トピックの管理
- `manage ons-subscriptions` - 通知購読の管理
- `read compartments` - コンパートメントの読み取り

### 3. OCI認証の設定

以下のいずれかの方法でOCI認証を設定してください：

#### 方法A: OCI CLI設定ファイル（推奨）

```bash
# OCI CLIの設定
oci setup config
```

#### 方法B: 環境変数

```bash
export TF_VAR_tenancy_ocid="ocid1.tenancy.oc1..aaaaaaaa..."
export TF_VAR_user_ocid="ocid1.user.oc1..aaaaaaaa..."
export TF_VAR_fingerprint="aa:bb:cc:dd:ee:ff:..."
export TF_VAR_private_key_path="/path/to/private/key.pem"
export TF_VAR_region="ap-osaka-1"
```

## デプロイ手順

### ステップ 1: リポジトリのクローンと移動

```bash
git clone <repository-url>
cd mystudy-handson/028.oci-cost-alert
```

### ステップ 2: 設定ファイルの準備

```bash
# サンプル設定ファイルをコピー
cp terraform.tfvars.example terraform.tfvars

# 設定ファイルを編集
vi terraform.tfvars  # または任意のエディタ
```

#### 必須設定項目

`terraform.tfvars`で以下の項目を必ず設定してください：

```hcl
# コンパートメントのOCID（必須）
compartment_id = "ocid1.compartment.oc1..your-actual-compartment-ocid"

# アラート通知先メールアドレス（必須）
alert_email_addresses = [
  "your-email@example.com",
  "finance@example.com"
]

# 予算金額（任意、デフォルト: 100）
budget_amount = 100

# アラート閾値（任意、デフォルト: 80%）
alert_threshold_percentage = 80
```

### ステップ 3: 自動デプロイ（推奨）

```bash
# デプロイスクリプトを実行可能にする
chmod +x deploy.sh

# 自動デプロイを実行
./deploy.sh
```

### ステップ 4: 手動デプロイ（上級者向け）

```bash
# 1. 初期化
terraform init

# 2. プランの確認
terraform plan

# 3. 適用
terraform apply
```

## デプロイ後の確認

### 1. メール確認の完了

デプロイ後、指定したメールアドレスに確認メールが送信されます：

1. 各メールアドレスで確認メールを確認
2. メール内の「Confirm subscription」リンクをクリック
3. 「Subscription confirmed」ページが表示されることを確認

### 2. OCI コンソールでの確認

1. [OCI コンソール](https://cloud.oracle.com/)にログイン
2. **Governance & Administration** > **Budgets** に移動
3. 作成された予算が表示されることを確認
4. 予算をクリックして、アラートルールが設定されていることを確認

### 3. 通知トピックの確認

1. **Developer Services** > **Notifications** に移動
2. 作成された通知トピックを確認
3. 購読者（メールアドレス）が「Confirmed」状態になっていることを確認

## トラブルシューティング

### よくある問題と解決方法

#### 1. 権限エラー

```
Error: 401-NotAuthenticated
```

**解決方法:**
- OCI認証設定を確認
- 必要な権限が付与されているか確認

#### 2. コンパートメントが見つからない

```
Error: 404-NotAuthorizedOrNotFound
```

**解決方法:**
- `compartment_id`が正しいか確認
- コンパートメントへのアクセス権限があるか確認

#### 3. メール確認が届かない

**解決方法:**
- スパムフォルダを確認
- メールアドレスが正しいか確認
- 企業のメールフィルタリング設定を確認

#### 4. Terraform初期化エラー

```
Error: Failed to install provider
```

**解決方法:**
```bash
# プロバイダーキャッシュをクリア
rm -rf .terraform
terraform init
```

### ログの確認

詳細なログを確認する場合：

```bash
# Terraformの詳細ログを有効化
export TF_LOG=DEBUG
terraform apply
```

## リソースの削除

### 自動削除（推奨）

```bash
# 削除スクリプトを実行可能にする
chmod +x destroy.sh

# 自動削除を実行
./destroy.sh
```

### 手動削除

```bash
# 削除プランの確認
terraform plan -destroy

# リソースの削除
terraform destroy
```

## セキュリティのベストプラクティス

### 1. 設定ファイルの管理

- `terraform.tfvars`をバージョン管理に含めない
- 機密情報は環境変数で管理する

### 2. 権限の最小化

- 必要最小限の権限のみを付与
- 定期的な権限の見直し

### 3. 通知の管理

- 適切な担当者のみにアラートを送信
- 定期的なメールアドレスの見直し

## 高度な設定

### 複数の予算アラート

複数の閾値でアラートを設定する場合：

```hcl
# 75%と90%でアラート
alert_threshold_percentage = 75

# 追加のアラートルールは手動で作成
```

### カスタムメッセージ

アラートメッセージをカスタマイズする場合は、`budget.tf`を編集してください。

## サポート

問題が発生した場合：

1. このガイドのトラブルシューティングセクションを確認
2. [OCI公式ドキュメント](https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/budgetsoverview.htm)を参照
3. GitHubリポジトリでIssueを作成