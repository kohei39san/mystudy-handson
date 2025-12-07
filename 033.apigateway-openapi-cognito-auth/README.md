# API Gateway + OpenAPI + Cognito + Lambda Authorizer

## 概要

このプロジェクトは、OpenAPI定義書を使用してAPI Gatewayを構築し、Cognito認証とLambdaオーソライザーによる役割ベースのアクセス制御を実装します。

## アーキテクチャ

### 主要コンポーネント

1. **Amazon Cognito User Pool**
   - ユーザー認証とカスタム属性（custom:role）の管理
   - PreTokenGenerationトリガーによる動的ロール割り当て

2. **API Gateway (REST API)**
   - OpenAPI定義書によるAPI仕様の管理
   - Cognitoオーソライザーとカスタムオーソライザーの組み合わせ
   - クエリパラメータのマッピング機能

3. **Lambda Functions**
   - **PreTokenGeneration Lambda**: Cognitoグループに基づくカスタムロールの設定
   - **Lambda Authorizer**: エンドポイント毎の役割ベースアクセス制御
   - **Backend Lambda**: APIエンドポイントの実装とクエリパラメータの処理

### 認証・認可フロー

1. ユーザーがCognitoでログイン
2. PreTokenGeneration Lambdaがユーザーのグループを確認し、custom:roleを設定
3. API Gatewayへのリクエスト時、Cognitoトークンで認証
4. Lambda Authorizerがトークン内のcustom:roleを検証
5. 適切な権限がある場合のみ、バックエンドLambdaが実行される

## ファイル構成

```
033.apigateway-openapi-cognito-auth/
├── README.md                    # このファイル
├── cfn/
│   └── infrastructure.yaml     # CloudFormationテンプレート
├── api/
│   └── openapi-spec.yaml       # OpenAPI定義書
└── scripts/
    ├── deploy.sh               # デプロイスクリプト
    └── test-api.py             # APIテストスクリプト
```

## デプロイ手順

1. **前提条件**
   - AWS CLI設定済み
   - 適切なIAM権限

2. **デプロイ実行**
   ```bash
   cd scripts
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **テスト実行**
   ```bash
   python test-api.py
   ```

## API エンドポイント

### 1. `/admin` (POST)
- **必要な役割**: admin
- **説明**: 管理者専用エンドポイント
- **クエリパラメータ**: `action`, `target`

### 2. `/user` (GET)
- **必要な役割**: user または admin
- **説明**: 一般ユーザー向けエンドポイント
- **クエリパラメータ**: `filter`, `limit`

### 3. `/public` (GET)
- **必要な役割**: なし（認証のみ）
- **説明**: 認証済みユーザー向け公開エンドポイント
- **クエリパラメータ**: `format`

## カスタム属性とロール

### custom:role の値
- `admin`: 管理者権限（全エンドポイントアクセス可能）
- `user`: 一般ユーザー権限（/user, /publicアクセス可能）
- `anonymous`: 匿名ユーザー（/publicのみアクセス可能）

### ロール割り当てルール
- `api-admins` グループ → `admin` ロール
- `api-users` グループ → `user` ロール
- グループ未所属 → `anonymous` ロール

## クエリパラメータマッピング

OpenAPI定義書内でAPI Gatewayのパラメータマッピング機能を使用し、以下の変換を行います：

1. **クエリパラメータの検証**: 必須パラメータのチェック
2. **デフォルト値の設定**: 未指定パラメータへのデフォルト値適用
3. **型変換**: 文字列から数値への変換
4. **Lambda統合**: マッピングされたパラメータをLambdaに渡す

## セキュリティ考慮事項

1. **多層防御**
   - Cognito認証 + Lambda Authorizer
   - IP制限（オプション）

2. **最小権限の原則**
   - 各ロールに必要最小限の権限のみ付与

3. **ログ記録**
   - 全ての認証・認可イベントをCloudWatch Logsに記録

## トラブルシューティング

### よくある問題

1. **403 Forbidden エラー**
   - Lambda Authorizerのロール検証を確認
   - Cognitoトークンのcustom:role属性を確認

2. **401 Unauthorized エラー**
   - Cognitoトークンの有効性を確認
   - Authorization ヘッダーの形式を確認

3. **クエリパラメータが渡されない**
   - OpenAPI定義書のパラメータマッピング設定を確認
   - API Gatewayのリクエスト変換設定を確認

## 参考資料

- [API Gateway OpenAPI Extensions](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions.html)
- [Cognito User Pool Lambda Triggers](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html)
- [Lambda Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-lambda-authorizer-lambda-function-create.html)