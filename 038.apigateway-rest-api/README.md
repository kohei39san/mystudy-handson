# API Gateway REST API シンプル構成

## 概要

このプロジェクトは、AWS API Gateway を使用してシンプルな REST API を構築するためのテンプレートです。基本的な API Gateway の機能を学習し、実装するための最小限の構成を提供します。

## アーキテクチャ

```
[クライアント] 
    ↓ (HTTP/HTTPS リクエスト)
[API Gateway REST API] 
    ↓ (モックレスポンス)
[レスポンス返却]
```

## 構成要素

### API Gateway
- **REST API**: RESTful API エンドポイント
- **リソース**: API のパス構造を定義
- **メソッド**: HTTP メソッド（GET, POST, PUT, DELETE）
- **モック統合**: Lambda を使わないシンプルなレスポンス
- **ステージ**: デプロイメント環境（dev, prod など）

### セキュリティ
- **CORS**: クロスオリジンリソース共有の設定
- **API キー**: オプションでアクセス制御
- **使用量プラン**: レート制限とクォータ

## クイックスタート

### 前提条件
- AWS CLI が設定済み
- 適切な AWS 権限を持つ IAM ユーザまたはロール

### CloudFormation でのデプロイ

1. **スタックの作成**
```bash
aws cloudformation create-stack \
  --stack-name apigateway-rest-api-demo \
  --template-body file://cfn/template.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev \
               ParameterKey=ProjectName,ParameterValue=my-api-project \
  --region ap-northeast-1
```

2. **デプロイ状況の確認**
```bash
aws cloudformation describe-stacks \
  --stack-name apigateway-rest-api-demo \
  --region ap-northeast-1
```

3. **API エンドポイントの取得**
```bash
aws cloudformation describe-stacks \
  --stack-name apigateway-rest-api-demo \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text \
  --region ap-northeast-1
```

## API エンドポイント

### 利用可能なエンドポイント

#### 1. ヘルスチェック
```bash
GET /health
```

**レスポンス例:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "service": "api-gateway-rest-api"
}
```

#### 2. 情報取得
```bash
GET /info
```

**レスポンス例:**
```json
{
  "message": "API Gateway REST API Demo",
  "version": "1.0.0",
  "environment": "dev"
}
```

#### 3. データ作成
```bash
POST /data
Content-Type: application/json

{
  "name": "sample",
  "value": "test"
}
```

**レスポンス例:**
```json
{
  "message": "Data created successfully",
  "id": "12345",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## テスト方法

### curl を使用したテスト

```bash
# API エンドポイント URL を取得
API_URL=$(aws cloudformation describe-stacks \
  --stack-name apigateway-rest-api-demo \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text \
  --region ap-northeast-1)

# ヘルスチェック
curl -X GET "${API_URL}/health"

# 情報取得
curl -X GET "${API_URL}/info"

# データ作成
curl -X POST "${API_URL}/data" \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "value": "sample"}'
```

## 設定オプション

### CloudFormation パラメータ

| パラメータ | 説明 | デフォルト値 |
|-----------|------|-------------|
| Environment | 環境名 | dev |
| ProjectName | プロジェクト名 | apigateway-rest-api |
| ApiName | API 名 | simple-rest-api |
| StageName | ステージ名 | dev |

## 運用管理

### ログの確認

```bash
# CloudWatch Logs で API Gateway のアクセスログを確認
aws logs describe-log-groups --log-group-name-prefix "API-Gateway-Execution-Logs"
```

### リソースの削除

```bash
aws cloudformation delete-stack \
  --stack-name apigateway-rest-api-demo \
  --region ap-northeast-1
```

## ファイル構成

```
038.apigateway-rest-api/
├── README.md                      # このファイル
├── cfn/
│   └── template.yaml              # CloudFormation テンプレート
└── openapi/
    └── base.yml                   # OpenAPI 仕様書
```

## 技術仕様

- **リージョン**: ap-northeast-1 (東京)
- **API タイプ**: REST API
- **統合方式**: モック統合
- **CloudFormation**: AWS::ApiGateway::*
- **OpenAPI**: 3.0.1

## 注意事項

- このテンプレートはデモ・学習目的です
- 本番環境では適切な認証・認可の実装を推奨します
- CORS 設定は必要に応じて調整してください
- API キーや使用量プランは要件に応じて設定してください

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。
