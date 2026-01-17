# API Gateway + OpenAPI + Cognito + Lambda Authorizer

## 概要

このプロジェクトは、OpenAPI定義書を使用してAPI Gatewayを構築し、Cognito認証とLambdaオーソライザーによる役割ベースのアクセス制御を実装します。

**038.apigateway-rest-apiの機能を統合済み：**
- OpenAPI仕様書の分割管理システム
- Python マージスクリプト
- GitHub Actions 自動マージワークフロー

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
├── README.md
├── cfn/
│   └── infrastructure.yaml      # CloudFormationテンプレート
├── openapi/                     # OpenAPI分割管理
│   ├── base.yml                 # ベース定義
│   ├── components/
│   │   └── schemas.yml          # スキーマ定義
│   └── paths/
│       ├── admin.yml            # 管理者エンドポイント
│       ├── user.yml             # ユーザーエンドポイント
│       ├── public.yml           # 公開エンドポイント
│       ├── health.yml           # ヘルスチェック
│       ├── login.yml            # ログインエンドポイント
│       ├── refresh.yml          # トークンリフレッシュエンドポイント
│       └── revoke.yml           # トークン無効化エンドポイント
├── src/
│   ├── openapi-spec.yaml        # OpenAPI仕様（レガシー）
│   ├── openapi-merged.yaml      # マージ済みOpenAPI仕様（自動生成）
│   └── users.csv                # ユーザーインポート用CSV
├── scripts/
│   ├── lambda/
│   │   ├── login.py             # ログインLambda関数
│   │   └── refresh.py           # リフレッシュLambda関数
│   ├── deploy.ps1               # デプロイスクリプト（PowerShell）
│   ├── update-lambda-code.ps1   # Lambda更新スクリプト
│   ├── merge-openapi.py         # OpenAPIマージスクリプト
│   ├── requirements.txt         # Python依存関係
│   ├── test-api-simple.py       # 簡易APIテスト
│   └── test-cognito-auth.py     # Cognito認証テスト
└── .github/
    └── workflows/
        └── merge-openapi.yml    # 自動マージワークフロー
```

## デプロイ手順

### 1. 前提条件
- AWS CLI設定済み
- PowerShell実行環境
- Python 3.x インストール済み

### 2. デプロイ実行

#### 方法1: OpenAPI分割管理を使用（推奨）

```powershell
cd 033.apigateway-openapi-cognito-auth

# Python依存関係のインストール
pip install -r scripts\requirements.txt

# OpenAPI仕様書をマージ
python scripts\merge-openapi.py --openapi-dir openapi --output src\openapi-merged.yaml

# デプロイ（自動的にマージされたファイルを使用）
powershell -ExecutionPolicy Bypass -File "scripts\deploy.ps1"
```

#### 方法2: レガシーOpenAPI仕様を使用

```powershell
cd 033.apigateway-openapi-cognito-auth
powershell -ExecutionPolicy Bypass -File "scripts\deploy.ps1"
```

デプロイスクリプトは以下を自動実行します：
1. OpenAPIファイルのマージ（openapi/ディレクトリが存在する場合）
2. CloudFormationスタックのデプロイ
3. CSVファイルからユーザーをインポート（ランダムパスワード生成）
4. OpenAPI仕様ファイルのプレースホルダー置換
5. API GatewayへのOpenAPI仕様インポート
6. Lambda関数コードの更新（scripts/lambda/*.pyから）
7. APIのデプロイ

### 3. APIテスト

```powershell
cd scripts
python test-api-simple.py --api-endpoint <API_ENDPOINT> --user-pool-id <USER_POOL_ID> --client-id <CLIENT_ID>
```

または

```powershell
python test-cognito-auth.py
```

## API エンドポイント

### 0. `/auth/login` (POST)
- **必要な役割**: なし（公開エンドポイント）
- **説明**: ユーザー名とパスワードでCognito認証を実行
- **リクエストボディ**: `username`, `password`
- **レスポンスヘッダー**: 
  - `Authorization`: AccessToken（API認証用）
  - `X-ID-Token`: IDToken（ユーザー識別情報）
  - `X-Refresh-Token`: RefreshToken（新しいトークン取得用）
  - `X-Expires-In`: トークン有効期限（秒）
- **レスポンスボディ**: `{"message": "Login successful"}`
- **エラー**: 401 (認証失敗), 404 (ユーザー未存在), 500 (サーバーエラー)

### 0. `/auth/refresh` (POST)
- **必要な役割**: なし（公開エンドポイント）
- **説明**: リフレッシュトークンを使用して新しいアクセストークンとIDトークンを取得
- **リクエストボディ**: `RefreshToken`
- **レスポンスヘッダー**: 
  - `Authorization`: AccessToken（API認証用）
  - `X-ID-Token`: IDToken（ユーザー識別情報）
  - `X-Expires-In`: トークン有効期限（秒）
- **レスポンスボディ**: `{"message": "Token refresh successful"}`
- **エラー**: 401 (無効なリフレッシュトークン), 404 (ユーザー未存在), 500 (サーバーエラー)

### 0. `/auth/revoke` (POST)
- **必要な役割**: admin
- **説明**: 管理者専用 - 指定ユーザーのトークンを無効化

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

## 認証フロー

### 1. ログイン
```bash
curl -X POST https://your-api-gateway-url/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TempPassword123!"}' \
  -i
```

レスポンスヘッダー:
```
Authorization: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
X-ID-Token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
X-Refresh-Token: eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ...
X-Expires-In: 3600
```

レスポンスボディ:
```json
{"message": "Login successful"}
```

### 2. トークンリフレッシュ
```bash
curl -X POST https://your-api-gateway-url/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"RefreshToken": "your-refresh-token"}' \
  -i
```

レスポンスヘッダー:
```
Authorization: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
X-ID-Token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
X-Expires-In: 3600
```

レスポンスボディ:
```json
{"message": "Token refresh successful"}
```

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

## OpenAPI仕様書の分割管理

### ファイル構成

- **base.yml**: OpenAPIの基本情報、セキュリティ定義
- **components/schemas.yml**: データモデルとスキーマ定義（LoginRequest、RefreshRequest、ErrorResponse等）
- **paths/login.yml**: ログインエンドポイントの定義
- **paths/refresh.yml**: トークンリフレッシュエンドポイントの定義
- **paths/revoke.yml**: トークン無効化エンドポイントの定義
- **paths/admin.yml**: 管理者エンドポイントの定義
- **paths/user.yml**: ユーザーエンドポイントの定義
- **paths/public.yml**: 公開エンドポイントの定義
- **paths/health.yml**: ヘルスチェックエンドポイントの定義

### プレースホルダーシステム

OpenAPIファイル内では以下のプレースホルダーを使用：
- `{{CognitoUserPoolArn}}`: Cognito User Pool ARN
- `{{LambdaAuthorizerUri}}`: Lambda Authorizer URI
- `{{BackendLambdaUri}}`: Backend Lambda URI
- `{{LoginLambdaUri}}`: Login Lambda URI
- `{{RefreshTokenLambdaUri}}`: Refresh Token Lambda URI
- `{{RevokeTokenLambdaUri}}`: Revoke Token Lambda URI
- `{{ApiGatewayRole}}`: API Gateway実行ロールARN

マージスクリプトまたはデプロイスクリプトが自動的に置換します。

### 手動マージ

```powershell
# 基本的なマージ（プレースホルダーはそのまま）
python scripts\merge-openapi.py

# 環境変数からプレースホルダーを置換してマージ
$env:COGNITO_USER_POOL_ARN = "arn:aws:cognito-idp:..."
$env:LAMBDA_AUTHORIZER_URI = "arn:aws:apigateway:..."
$env:BACKEND_LAMBDA_URI = "arn:aws:apigateway:..."
$env:LOGIN_LAMBDA_URI = "arn:aws:apigateway:..."
$env:REFRESH_TOKEN_LAMBDA_URI = "arn:aws:apigateway:..."
$env:REVOKE_TOKEN_LAMBDA_URI = "arn:aws:apigateway:..."
$env:API_GATEWAY_ROLE_ARN = "arn:aws:iam::..."
python scripts\merge-openapi.py --replace-placeholders
```

### 自動マージ（GitHub Actions）

GitHub Actionsワークフローが以下の場合に自動実行されます：
- `openapi/**/*.yml` ファイルの変更時
- `scripts/merge-openapi.py` の変更時
- マージされた `src/openapi-merged.yaml` ファイルを自動コミット

## セキュリティ考慮事項

1. **多層防御**
   - Cognito認証 + Lambda Authorizer
   - IP制限（オプション）

2. **最小権限の原則**
   - 各ロールに必要最小限の権限のみ付与

3. **ログ記録**
   - 全ての認証・認可イベントをCloudWatch Logsに記録

## Lambda関数コードの管理

### 外部Pythonスクリプト

Login/RefreshのLambda関数コードは `scripts/lambda/` ディレクトリで管理：
- `scripts/lambda/login.py`: ログイン処理（トークンをヘッダーで返却）
- `scripts/lambda/refresh.py`: トークンリフレッシュ処理（トークンをヘッダーで返却）

### デプロイ時の自動更新

`scripts/deploy.ps1` 実行時に自動的にLambda関数コードが更新されます。

### 個別更新

Lambda関数コードのみを更新する場合：
```powershell
.\scripts\update-lambda-code.ps1 -StackName "openapi-cognito-auth-dev"
```

## ユーザー管理

### CSVファイルからのインポート

`src/users.csv`にユーザー情報を記載：
```csv
username,group
testuser,api-users
adminuser,api-admins
```

- パスワードは自動生成され、デプロイ時に表示されます
- グループに基づいてcustom:roleが自動設定されます

## トラブルシューティング

### デプロイエラー

**OpenAPIインポートエラー**: "A combination of multiple Authorizers..."
- 原因: 複数のAuthorizerを同時に指定
- 解決: CognitoUserPoolのみを使用

**デプロイメントエラー**: "The REST API doesn't contain any methods"
- 原因: メソッドが定義されていない状態でデプロイ
- 解決: OpenAPIインポート後にデプロイ

**httpMethodエラー**: "Enumeration value for HttpMethod must be non-empty"
- 原因: Lambda統合にhttpMethodが未指定
- 解決: `httpMethod: POST`を追加

### 認証エラー

**403 Forbidden エラー**
- Lambda Authorizerのロール検証を確認
- Cognitoトークンのcustom:role属性を確認

**401 Unauthorized エラー**
- Cognitoトークンの有効性を確認
- Authorization ヘッダーの形式を確認

### その他

**クエリパラメータが渡されない**
- OpenAPI定義書のパラメータマッピング設定を確認
- API Gatewayのリクエスト変換設定を確認

## クリーンアップ

```powershell
aws cloudformation delete-stack --stack-name openapi-cognito-auth-dev
```

## 参考資料

- [API Gateway OpenAPI Extensions](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions.html)
- [Cognito User Pool Lambda Triggers](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html)
- [Lambda Authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-lambda-authorizer-lambda-function-create.html)