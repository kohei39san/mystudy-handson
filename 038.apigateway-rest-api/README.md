# AWS API Gateway REST API デプロイメント

## 概要

このプロジェクトは、CloudFormationを使用してAWS API Gateway REST APIをデプロイし、OpenAPI仕様書を分割管理するためのツールとワークフローを提供します。

## アーキテクチャ

### 主要コンポーネント

1. **Amazon API Gateway (REST API)**
   - OpenAPI仕様書による API 定義
   - Lambda統合によるバックエンド処理
   - CORS設定とエラーハンドリング

2. **AWS Lambda Functions**
   - **Backend Lambda**: APIエンドポイントの実装
   - ヘルスチェックとユーザー管理機能

3. **OpenAPI仕様書の分割管理**
   - ベース定義、スキーマ、パス定義を分離
   - Python スクリプトによる自動マージ
   - GitHub Actions による自動化

## ファイル構成

```
038.apigateway-rest-api/
├── README.md
├── cfn/
│   └── template.yaml              # CloudFormationテンプレート
├── openapi/
│   ├── base.yml                   # OpenAPIベース定義
│   ├── components/
│   │   └── schemas.yml            # スキーマ定義
│   └── paths/
│       ├── users.yml              # ユーザーエンドポイント
│       └── health.yml             # ヘルスチェックエンドポイント
├── scripts/
│   ├── merge-openapi.py           # OpenAPIマージスクリプト
│   └── requirements.txt           # Python依存関係
└── .github/
    └── workflows/
        └── merge-openapi.yml      # GitHub Actionsワークフロー
```

## デプロイ手順

### 1. 前提条件
- AWS CLI設定済み
- 適切なIAM権限
- Python 3.x インストール済み

### 2. CloudFormationデプロイ

```bash
cd 038.apigateway-rest-api

# CloudFormationスタックのデプロイ
aws cloudformation deploy \
  --template-file cfn/template.yaml \
  --stack-name apigateway-rest-api-dev \
  --parameter-overrides Environment=dev \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-1
```

### 3. OpenAPI仕様書のマージとデプロイ

```bash
# 依存関係のインストール
pip install -r scripts/requirements.txt

# OpenAPI仕様書のマージ（プレースホルダー置換なし）
python scripts/merge-openapi.py

# CloudFormationの出力値を取得
STACK_NAME="apigateway-rest-api-dev"
API_ID=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayRestApiId`].OutputValue' \
  --output text \
  --region ap-northeast-1)

BACKEND_LAMBDA_ARN=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`BackendLambdaArn`].OutputValue' \
  --output text \
  --region ap-northeast-1)

API_GATEWAY_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayRoleArn`].OutputValue' \
  --output text \
  --region ap-northeast-1)

# プレースホルダーを置換してマージ
export AWS_REGION="ap-northeast-1"
export BACKEND_LAMBDA_ARN="$BACKEND_LAMBDA_ARN"
export API_GATEWAY_ROLE_ARN="$API_GATEWAY_ROLE_ARN"

python scripts/merge-openapi.py --replace-placeholders

# API Gatewayへのデプロイ
aws apigateway put-rest-api \
  --rest-api-id $API_ID \
  --mode overwrite \
  --body file://openapi.yml \
  --region ap-northeast-1

# デプロイメントの作成
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name dev \
  --region ap-northeast-1
```

## API エンドポイント

### 1. `/health` (GET)
- **説明**: ヘルスチェックエンドポイント
- **認証**: 不要
- **レスポンス**: システムの稼働状況

### 2. `/users` (GET)
- **説明**: ユーザー一覧取得
- **認証**: 必要
- **クエリパラメータ**: 
  - `limit`: 取得件数制限
  - `offset`: オフセット

### 3. `/users` (POST)
- **説明**: ユーザー作成
- **認証**: 必要
- **リクエストボディ**: ユーザー情報

### 4. `/users/{id}` (GET)
- **説明**: 特定ユーザー取得
- **認証**: 必要
- **パスパラメータ**: `id` - ユーザーID

## OpenAPI仕様書の分割管理

### ファイル構成

- **base.yml**: OpenAPIの基本情報、サーバー設定、セキュリティ定義
- **components/schemas.yml**: データモデルとスキーマ定義
- **paths/health.yml**: ヘルスチェックエンドポイントの定義
- **paths/users.yml**: ユーザー関連エンドポイントの定義

### プレースホルダーシステム

OpenAPIファイル内では以下のプレースホルダーを使用：
- `{{AWS_REGION}}`: AWSリージョン
- `{{BACKEND_LAMBDA_ARN}}`: バックエンドLambda関数のARN
- `{{API_GATEWAY_ROLE_ARN}}`: API Gateway実行ロールのARN

マージスクリプトが環境変数から値を取得して置換します。

### 自動マージ機能

GitHub Actionsワークフローが以下の場合に自動実行されます：
- `openapi/**/*.yml` ファイルの変更時
- マージされた `openapi.yml` ファイルを自動コミット

## セキュリティ考慮事項

1. **認証・認可**
   - API Keyによる認証
   - IAMロールベースのアクセス制御

2. **CORS設定**
   - 適切なオリジン制限
   - プリフライトリクエストの処理

3. **入力検証**
   - OpenAPIスキーマによるリクエスト検証
   - SQLインジェクション対策

## トラブルシューティング

### デプロイエラー

**CloudFormationエラー**: スタック作成失敗
- IAM権限の確認
- リソース名の重複確認

**OpenAPIマージエラー**: YAML構文エラー
- 各YAMLファイルの構文確認
- インデントの確認

**プレースホルダー置換エラー**: 環境変数未設定
- 必要な環境変数の設定確認
- CloudFormationスタックの出力値確認

### API実行エラー

**403 Forbidden**: 認証エラー
- API Keyの確認
- IAMロールの権限確認

**500 Internal Server Error**: Lambda実行エラー
- CloudWatch Logsの確認
- Lambda関数の設定確認

## クリーンアップ

```bash
aws cloudformation delete-stack \
  --stack-name apigateway-rest-api-dev \
  --region ap-northeast-1
```
