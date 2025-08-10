# OCI コストアラート - ファイル構成一覧

このディレクトリには、Oracle Cloud Infrastructure (OCI) でコストアラート機能を実装するためのTerraformコードとサポートファイルが含まれています。

## 📁 ファイル構成

### 🔧 Terraform設定ファイル

| ファイル名 | 説明 | 必須 |
|-----------|------|------|
| `terraform.tf` | Terraformプロバイダーとバージョン設定 | ✅ |
| `variables.tf` | 入力変数の定義 | ✅ |
| `budget.tf` | 予算とアラートルールのリソース定義 | ✅ |
| `notification.tf` | 通知トピックとメール購読のリソース定義 | ✅ |
| `outputs.tf` | 出力値の定義 | ✅ |

### 📋 設定ファイル

| ファイル名 | 説明 | 必須 |
|-----------|------|------|
| `terraform.tfvars.example` | 設定例ファイル（実際の設定用にコピーして使用） | ✅ |
| `.gitignore` | Gitで管理しないファイルの指定 | ✅ |

### 📚 ドキュメント

| ファイル名 | 説明 | 言語 |
|-----------|------|------|
| `README.md` | プロジェクトの概要と使用方法 | 日本語 |
| `DEPLOYMENT_GUIDE.md` | 詳細なデプロイメントガイド | 日本語 |
| `FILES_SUMMARY.md` | このファイル - ファイル構成の説明 | 日本語 |

### 🚀 デプロイメントスクリプト

| ファイル名 | 説明 | 実行権限 |
|-----------|------|---------|
| `deploy.sh` | 自動デプロイスクリプト | 要実行権限 |
| `destroy.sh` | 自動削除スクリプト | 要実行権限 |

### 🧪 テストスクリプト

| ファイル名 | 説明 | 実行権限 |
|-----------|------|---------|
| `test_validation.sh` | 基本的な設定検証テスト | 要実行権限 |
| `test_comprehensive.sh` | 包括的なテストスイート | 要実行権限 |

## 🔄 ファイルの依存関係

```
terraform.tf
├── variables.tf (変数定義を参照)
├── budget.tf (変数を使用してリソース作成)
├── notification.tf (変数を使用してリソース作成)
└── outputs.tf (リソースの出力値を定義)

terraform.tfvars.example
└── terraform.tfvars (ユーザーが作成する実際の設定ファイル)

deploy.sh
├── test_validation.sh (検証テストを実行)
├── terraform.tfvars (設定ファイルの存在確認)
└── terraform.tf (Terraformコマンドを実行)
```

## 📝 各ファイルの詳細

### Terraform設定ファイル

#### `terraform.tf`
- OCIプロバイダーの設定
- Terraformバージョン要件の定義
- プロバイダーバージョンの指定

#### `variables.tf`
- 全ての入力変数の定義
- デフォルト値の設定
- 変数の説明とタイプ定義

#### `budget.tf`
- `oci_budget_budget`: 予算リソースの定義
- `oci_budget_alert_rule`: アラートルールの定義
- 予算額と閾値の設定

#### `notification.tf`
- `oci_ons_notification_topic`: 通知トピックの定義
- `oci_ons_subscription`: メール購読の定義
- 複数メールアドレスへの対応

#### `outputs.tf`
- 作成されたリソースのIDと情報を出力
- デプロイ後の確認に使用

### スクリプトファイル

#### `deploy.sh`
- 自動デプロイメントスクリプト
- 設定ファイルの検証
- Terraformコマンドの実行
- エラーハンドリング

#### `destroy.sh`
- 安全なリソース削除スクリプト
- 確認プロンプト付き
- 削除前の警告表示

#### `test_validation.sh`
- 基本的な設定検証
- ファイル存在確認
- Terraform構文チェック

#### `test_comprehensive.sh`
- 包括的なテストスイート
- 50以上のテストケース
- 詳細な結果レポート

## 🚀 使用開始手順

1. **設定ファイルの準備**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # terraform.tfvarsを編集
   ```

2. **スクリプトに実行権限を付与**
   ```bash
   chmod +x *.sh
   ```

3. **テストの実行**
   ```bash
   ./test_comprehensive.sh
   ```

4. **デプロイの実行**
   ```bash
   ./deploy.sh
   ```

## 🔒 セキュリティ考慮事項

- `terraform.tfvars`は`.gitignore`に含まれており、バージョン管理されません
- 機密情報（OCID、メールアドレス）は設定ファイルで管理
- スクリプトには適切なエラーハンドリングが実装されています

## 📊 リソース作成内容

このTerraformコードは以下のOCIリソースを作成します：

1. **予算 (Budget)**: 指定金額での予算設定
2. **予算アラートルール (Budget Alert Rule)**: 閾値超過時のアラート
3. **通知トピック (Notification Topic)**: アラート配信用トピック
4. **メール購読 (Email Subscriptions)**: 指定メールアドレスへの通知設定

## 🆘 サポート

問題が発生した場合：
1. `README.md`のトラブルシューティングセクションを確認
2. `DEPLOYMENT_GUIDE.md`の詳細手順を参照
3. テストスクリプトでエラーの詳細を確認
4. GitHubリポジトリでIssueを作成