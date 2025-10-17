# デプロイメントガイド

## 概要
このガイドでは、API Gateway + Cognito + Lambda ペイロード検証システムのデプロイ手順を詳しく説明します。

## 前提条件の確認

### 必要なツール
```bash
# AWS CLI のバージョン確認
aws --version

# Terraform のバージョン確認
terraform --version

# Python のバージョン確認（テスト用）
python3 --version
```

### AWS 認証情報の設定
```bash
# AWS 認証情報の確認
aws sts get-caller-identity

# 必要に応じて設定
aws configure
```

### 必要な AWS 権限
デプロイには以下の権限が必要です：
- CloudFormation: フルアクセス
- IAM: ロール・ポリシー作成権限
- Cognito: フルアクセス
- API Gateway: フルアクセス
- Lambda: フルアクセス
- CloudWatch Logs: フルアクセス

## ステップバイステップデプロイ

### ステップ 1: プロジェクトディレクトリへの移動
```bash
cd 030.apigateway-cognito-lambda-payload
```

### ステップ 2: 設定ファイルの準備
```bash
# 設定例ファイルをコピー
cp terraform.tfvars.example terraform.tfvars

# 設定ファイルを編集
nano terraform.tfvars
```

**重要な設定項目:**
```hcl
# 環境名（リソース名に使用）
environment = "dev"

# Cognito ユーザのメールアドレス
user_email = "your-email@example.com"

# 許可する IP アドレス（セキュリティ重要！）
allowed_ip_addresses = ["YOUR_IP_ADDRESS/32"]
```

### ステップ 3: IP アドレスの確認
```bash
# 現在の IP アドレスを確認
curl -s https://checkip.amazonaws.com
```

### ステップ 4: Terraform の初期化
```bash
terraform init
```

### ステップ 5: デプロイ計画の確認
```bash
terraform plan -var-file=terraform.tfvars
```

### ステップ 6: インフラストラクチャのデプロイ
```bash
terraform apply -var-file=terraform.tfvars
```

### ステップ 7: Cognito ユーザのパスワード設定
```bash
# Terraform の出力から値を取得
USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
USER_EMAIL=$(terraform output -raw deployment_info | jq -r '.user_email')

# パスワードを設定
aws cognito-idp admin-set-user-password \
  --user-pool-id "$USER_POOL_ID" \
  --username "$USER_EMAIL" \
  --password 'TempPassword123!' \
  --permanent \
  --region ap-northeast-1
```

## 自動デプロイ（推奨）

### 自動デプロイスクリプトの使用
```bash
# スクリプトに実行権限を付与
chmod +x deploy.sh

# 自動デプロイの実行
./deploy.sh
```

スクリプトが以下を自動実行：
1. 前提条件のチェック
2. 設定情報の対話的入力
3. Terraform によるデプロイ
4. Cognito ユーザのパスワード設定
5. 自動テストの実行（オプション）

## デプロイ後の確認

### 1. リソースの確認
```bash
# デプロイされたリソースの確認
terraform output

# CloudFormation スタックの確認
aws cloudformation describe-stacks --stack-name apigateway-cognito-lambda-dev
```

### 2. API エンドポイントの確認
```bash
# API Gateway URL の取得
API_URL=$(terraform output -raw api_gateway_url)
echo "API Gateway URL: $API_URL"
```

### 3. Cognito 設定の確認
```bash
# User Pool の確認
USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
aws cognito-idp describe-user-pool --user-pool-id "$USER_POOL_ID"
```

## テストの実行

### 自動テストスクリプト
```bash
# Python 依存関係のインストール
pip install -r requirements.txt

# テストの実行
python test-api.py \
  --user-pool-id $(terraform output -raw cognito_user_pool_id) \
  --client-id $(terraform output -raw cognito_user_pool_client_id) \
  --api-url $(terraform output -raw api_gateway_url) \
  --username $(terraform output -raw deployment_info | jq -r '.user_email') \
  --password 'TempPassword123!'
```

### 手動テスト
```bash
# 1. Cognito 認証（JWT トークン取得）
aws cognito-idp admin-initiate-auth \
  --user-pool-id "$USER_POOL_ID" \
  --client-id "$CLIENT_ID" \
  --auth-flow ADMIN_NO_SRP_AUTH \
  --auth-parameters USERNAME="$USER_EMAIL",PASSWORD="TempPassword123!"

# 2. API 呼び出し
curl -X GET \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  "$API_URL/test"
```

## ログの確認

### CloudWatch Logs でのログ確認
```bash
# Lambda 関数名の取得
FUNCTION_NAME=$(terraform output -raw lambda_function_name)

# ログストリームの確認
aws logs describe-log-streams \
  --log-group-name "/aws/lambda/$FUNCTION_NAME" \
  --order-by LastEventTime \
  --descending

# 最新のログイベント取得
aws logs get-log-events \
  --log-group-name "/aws/lambda/$FUNCTION_NAME" \
  --log-stream-name "LATEST_STREAM_NAME"
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. IP アドレス制限エラー
**エラー**: `403 Forbidden` レスポンス
**解決方法**:
```bash
# 現在の IP を確認
curl -s https://checkip.amazonaws.com

# terraform.tfvars を更新
# allowed_ip_addresses = ["YOUR_NEW_IP/32"]

# 再デプロイ
terraform apply -var-file=terraform.tfvars
```

#### 2. Cognito 認証エラー
**エラー**: `NotAuthorizedException`
**解決方法**:
```bash
# ユーザの状態確認
aws cognito-idp admin-get-user \
  --user-pool-id "$USER_POOL_ID" \
  --username "$USER_EMAIL"

# パスワードの再設定
aws cognito-idp admin-set-user-password \
  --user-pool-id "$USER_POOL_ID" \
  --username "$USER_EMAIL" \
  --password 'NewPassword123!' \
  --permanent
```

#### 3. Lambda 実行エラー
**解決方法**:
```bash
# Lambda 関数のログを確認
aws logs filter-log-events \
  --log-group-name "/aws/lambda/$FUNCTION_NAME" \
  --start-time $(date -d '1 hour ago' +%s)000
```

#### 4. API Gateway デプロイエラー
**解決方法**:
```bash
# API Gateway のデプロイ状況確認
aws apigateway get-deployments --rest-api-id "$API_ID"

# 手動でデプロイメント作成
aws apigateway create-deployment \
  --rest-api-id "$API_ID" \
  --stage-name dev
```

## リソースの削除

### 完全削除
```bash
# 自動削除
./deploy.sh destroy

# または手動削除
terraform destroy -var-file=terraform.tfvars
```

### 部分的な削除
```bash
# 特定のリソースのみ削除
terraform destroy -target=aws_cloudformation_stack.infrastructure
```

## セキュリティのベストプラクティス

### 1. IP アドレス制限の適切な設定
```hcl
# 悪い例
allowed_ip_addresses = ["0.0.0.0/0"]

# 良い例
allowed_ip_addresses = ["203.0.113.100/32", "198.51.100.0/24"]
```

### 2. 強力なパスワードポリシー
本番環境では、より厳しいパスワードポリシーを設定：
```yaml
PasswordPolicy:
  MinimumLength: 12
  RequireUppercase: true
  RequireLowercase: true
  RequireNumbers: true
  RequireSymbols: true
```

### 3. MFA の有効化
```bash
# MFA デバイスの設定
aws cognito-idp admin-set-user-mfa-preference \
  --user-pool-id "$USER_POOL_ID" \
  --username "$USER_EMAIL" \
  --sms-mfa-settings Enabled=true,PreferredMfa=true
```

## 監視とアラート

### CloudWatch アラームの設定
```bash
# Lambda エラー率のアラーム
aws cloudwatch put-metric-alarm \
  --alarm-name "Lambda-Error-Rate" \
  --alarm-description "Lambda function error rate" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold
```

## 参考資料

- [AWS Cognito ドキュメント](https://docs.aws.amazon.com/cognito/)
- [API Gateway ドキュメント](https://docs.aws.amazon.com/apigateway/)
- [Lambda ドキュメント](https://docs.aws.amazon.com/lambda/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)