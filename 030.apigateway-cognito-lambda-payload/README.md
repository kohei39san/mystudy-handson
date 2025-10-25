# API Gateway + Cognito + Lambda ペイロード検証システム

## 概要

このプロジェクトは、AWS API Gateway、Cognito ユーザプール、Lambda を使用してペイロード検証システムを構築します。Cognito による認証を通じて、Lambda 関数のイベントペイロードをログ出力するシステムに加えて、Cognito認証時にユーザーグループに基づいてカスタム属性を自動設定する機能を提供します。

## アーキテクチャ

```
[クライアント] 
    ↓ (認証トークン)
[API Gateway REST API] 
    ↓ (Cognito オーソライザー)
[Lambda 関数 (ペイロードログ)] 
    ↓ (ログ出力)
[CloudWatch Logs]

[Cognito認証イベント]
    ↓ (Pre Token Generation トリガー)
[Lambda 関数 (カスタム属性設定)]
    ↓ (グループベースのロール設定)
[Cognito ユーザー属性更新]
```

## 構成要素

### AWS Cognito
- **ユーザプール**: ユーザ認証を管理
- **カスタム属性**: ユーザーのロール情報を格納する `custom:role` 属性
- **ユーザプールクライアント**: シングルページアプリケーション用の設定
- **ユーザグループ**: IAM ロールが紐づけられたユーザグループ
- **Lambda トリガー**: Pre Token Generation イベントでカスタム属性を設定
- **IAM ロール**: Cognito ユーザに割り当てられる権限

### API Gateway
- **REST API**: RESTful API エンドポイント
- **リソースポリシー**: 指定 IP アドレス以外からのアクセスを拒否
- **Cognito オーソライザー**: Cognito ユーザプールによる認証
- **プロキシ統合**: Lambda 関数との統合

### Lambda
- **ペイロードログ関数**: Python で実装されたシンプルなログ出力関数
- **カスタム属性設定関数**: Cognito認証時にユーザーグループに基づいてロールを設定
- **IAM ロール**: Lambda 実行に必要な権限
- **CloudWatch Logs**: ログ出力先

## カスタム属性機能

### ロール設定ロジック
- **api-users グループのメンバー**: `custom:role` = "admin"
- **その他のユーザー**: `custom:role` = "anonymous"

### 動作タイミング
- Cognito の Pre Token Generation トリガーで実行
- JWT トークンにカスタムクレームとして `custom:role` を追加
- ユーザー属性としても永続化

## クイックスタート

### 前提条件
- AWS CLI が設定済み
- Terraform がインストール済み
- 適切な AWS 権限を持つ IAM ユーザまたはロール

### 手順

1. **設定ファイルの作成**
```bash
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars を編集して環境に合わせて設定
```

2. **Terraform の初期化と実行**
```bash
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

3. **Cognito ユーザのパスワード設定**
```bash
# Terraform の出力から USER_POOL_ID と USER_EMAIL を取得
aws cognito-idp admin-set-user-password \
  --user-pool-id <USER_POOL_ID> \
  --username <USER_EMAIL> \
  --password 'TempPassword123!' \
  --permanent \
  --region ap-northeast-1
```

## テスト方法

### 手動テスト

1. **Cognito 認証**
   - AWS CLI または SDK を使用して JWT トークンを取得

2. **API 呼び出し**
```bash
curl -X GET \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  "<API_GATEWAY_URL>/test"
```

```powershell
python scripts\test-api.py --user-pool-id <USER_POOL_ID> --client-id <CLIENT_ID> --api-url https://<API_GATEWAY_ENDPOINT>/dev --username <USER_NAME> --password "TempPassword123!"
```

3. **ログ確認**
   - CloudWatch Logs で Lambda 関数のログを確認

## 設定オプション

### terraform.tfvars の主要設定

```hcl
# 環境名
environment = "dev"

# ユーザメールアドレス
user_email = "your-email@example.com"

# 許可する IP アドレス（セキュリティ重要）
allowed_ip_addresses = ["203.0.113.0/24", "198.51.100.0/24"]

# プロジェクト名
project_name = "my-api-project"
```

### セキュリティ設定

**重要**: `allowed_ip_addresses` を適切に設定してください：

```hcl
# 悪い例（全てのIPを許可）
allowed_ip_addresses = ["0.0.0.0/0"]

# 良い例（特定のIPのみ許可）
allowed_ip_addresses = ["203.0.113.100/32", "198.51.100.0/24"]
```

## 運用管理

### ログの確認

```bash
# CloudWatch Logs でLambda関数のログを確認
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/"
aws logs get-log-events --log-group-name "/aws/lambda/<FUNCTION_NAME>"
```

### リソースの削除

```bash
terraform destroy -var-file=terraform.tfvars
```

### トラブルシューティング

#### 認証エラー
- Cognito ユーザのパスワードが正しく設定されているか確認
- JWT トークンの有効期限を確認

#### API アクセスエラー
- IP アドレス制限の設定を確認
- API Gateway のデプロイ状況を確認

#### Lambda エラー
- CloudWatch Logs でエラーメッセージを確認
- IAM ロールの権限を確認

## ファイル構成

```
030.apigateway-cognito-lambda-payload/
├── README.md                      # このファイル
├── main.tf                        # メインの Terraform 設定
├── variables.tf                   # 変数定義
├── outputs.tf                     # 出力定義
├── provider.tf                    # プロバイダー設定
├── terraform.tfvars.example       # 設定例ファイル
└── cfn/                           # CloudFormation テンプレート
    └── infrastructure.yaml        # インフラストラクチャ定義
```

## 技術仕様

- **リージョン**: ap-northeast-1 (東京)
- **API タイプ**: REST API
- **認証方式**: Cognito ユーザプール
- **統合方式**: Lambda プロキシ統合
- **ランタイム**: Python 3.9
- **Terraform**: >= 1.0
- **AWS Provider**: ~> 5.0
- **Cognito トリガー**: Pre Token Generation
- **カスタム属性**: custom:role (String型、可変)

## カスタム属性の監視とトラブルシューティング

### ログの確認

```bash
# カスタム属性Lambda関数のログを確認
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/" | grep cognito-custom-attribute
aws logs get-log-events --log-group-name "/aws/lambda/<CUSTOM_ATTRIBUTE_FUNCTION_NAME>"
```

### カスタム属性の動作確認

```bash
# ユーザーの属性を確認
aws cognito-idp admin-get-user \
  --user-pool-id <USER_POOL_ID> \
  --username <USER_EMAIL> \
  --region ap-northeast-1

# ユーザーのグループメンバーシップを確認
aws cognito-idp admin-list-groups-for-user \
  --user-pool-id <USER_POOL_ID> \
  --username <USER_EMAIL> \
  --region ap-northeast-1
```

### トラブルシューティング

#### カスタム属性が設定されない場合
- Lambda関数のCloudWatch Logsでエラーメッセージを確認
- IAMロールにCognito操作権限が付与されているか確認
- Cognito User PoolのLambda Triggersが正しく設定されているか確認

#### 認証エラー
- Cognito ユーザのパスワードが正しく設定されているか確認
- JWT トークンの有効期限を確認
- カスタムクレーム `custom:role` がトークンに含まれているか確認

## セキュリティ

- **IP 制限**: API Gateway のリソースポリシーにより、指定された IP アドレス以外からのアクセスを拒否
- **認証**: Cognito ユーザプールによる JWT トークン認証
- **最小権限**: IAM ロールは最小限の権限のみを付与
- **暗号化**: AWS のマネージド暗号化を使用

## 注意事項

- IP アドレス制限は `allowed_ip_addresses` 変数で設定してください
- Cognito ユーザのメールアドレスは `user_email` 変数で指定してください
- Lambda 関数は受信したイベントをそのままログ出力するため、機密情報が含まれる場合は注意してください
- 本番環境では、より強固なパスワードポリシーと MFA の設定を推奨します
- **カスタム属性機能**: ユーザーのロール情報は JWT トークンに含まれるため、クライアント側で参照可能です
- **グループ変更**: ユーザーのグループメンバーシップが変更された場合、次回認証時にロールが自動更新されます
- **Lambda エラー**: カスタム属性設定でエラーが発生しても認証は継続されますが、ロール情報が正しく設定されない可能性があります

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。