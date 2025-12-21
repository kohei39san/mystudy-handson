# Aurora Mock Testing Project - 詳細ドキュメント

## プロジェクト概要

このプロジェクトは、Aurora PostgreSQL、Secrets Manager、ECS、Lambdaを使用したシステムのモックテストを実装するためのものです。IAMトークン認証を使用したPostgreSQLユーザーの作成と、各AWSサービスの統合テストを含みます。

## アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Lambda      │    │  Secrets Mgr    │    │   Aurora PG     │
│  (Data Access)  │◄──►│ (DB Credentials)│    │  (Database)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              ▲
         │                                              │
         ▼                                              │
┌─────────────────┐                            ┌─────────────────┐
│      ECS        │                            │  IAM Token      │
│  (Flask API)    │                            │ Authentication  │
└─────────────────┘                            └─────────────────┘
```

## ディレクトリ構成

```
035.aurora-mock-testing/
├── README.md                 # プロジェクト概要
├── DOCUMENTATION.md          # 詳細ドキュメント（このファイル）
├── requirements.txt          # Python依存関係
├── pytest.ini              # pytest設定
├── Makefile                 # プロジェクト管理用Makefile
├── .gitignore              # Git除外ファイル
├── .env.example            # 環境変数サンプル
│
├── main.tf                  # Terraform メイン設定
├── variables.tf             # Terraform 変数定義
├── outputs.tf               # Terraform 出力定義
├── provider.tf              # Terraform プロバイダー設定
│
├── cfn/                     # CloudFormation テンプレート
│   ├── aurora.yaml          # Aurora Serverless設定
│   ├── secrets-manager.yaml # Secrets Manager設定
│   ├── ecs.yaml            # ECS設定
│   └── lambda.yaml         # Lambda設定
│
├── scripts/                 # スクリプトファイル
│   ├── deploy.sh           # デプロイスクリプト
│   └── lambda_function.py  # Lambda関数コード
│
└── tests/                   # 単体テストファイル
    ├── conftest.py         # pytest設定とフィクスチャ
    └── test_lambda_function.py # Lambda関数テスト
```

## 技術仕様

### AWS リソース

#### CloudFormation で管理するリソース
- **Aurora Serverless v2 (PostgreSQL 15.4)**
  - IAMトークン認証有効
  - 最小容量: 0.5 ACU
  - 最大容量: 1 ACU
  - 暗号化有効

- **Secrets Manager**
  - Aurora接続情報を保存
  - Lambda/ECSからアクセス可能

- **ECS Fargate**
  - Flask REST APIをホスト
  - Application Load Balancer付き
  - CloudWatch Logs統合

- **Lambda**
  - Python 3.9ランタイム
  - VPC内配置
  - Aurora、Secrets Manager、ECSへのアクセス

#### Terraform で管理するリソース
- **IAM Role/Policy**
  - RDS IAMトークン認証用
  - Lambda実行用
  - ECSタスク用

- **IAM User**
  - PostgreSQL IAMトークン認証用

### セキュリティ設定

#### ネットワークセキュリティ
- VPC内でのプライベート通信
- セキュリティグループによる最小権限アクセス
- Aurora: Lambda/ECSからのみアクセス可能
- ECS: インターネットからHTTP/HTTPSアクセス可能

#### IAM権限
- Lambda: Secrets Manager読み取り、RDS接続、VPC実行権限
- ECS: RDS接続権限
- IAMユーザー: RDS IAMトークン認証権限

## テスト戦略

### モック化対象

1. **boto3.client (moto使用)**
   ```python
   from moto import mock_secretsmanager, mock_rds
   
   @mock_secretsmanager
   def test_secrets_manager():
       # Secrets Managerのモック化
   ```

2. **psycopg2 (unittest.mock使用)**
   ```python
   @patch('lambda_function.psycopg2')
   def test_database_connection(mock_psycopg2):
       # データベース接続のモック化
   ```

3. **環境変数 (pytest monkeypatch使用)**
   ```python
   def test_with_env_vars(monkeypatch):
       monkeypatch.setenv('AURORA_SECRET_ARN', 'test-arn')
   ```

### テストカテゴリ

#### 単体テスト
- Lambda関数の各機能
- エラーハンドリング
- AWS SDK呼び出し

#### 統合テスト
- motoを使用したAWSサービス統合
- エンドツーエンドワークフロー

## セットアップ手順

### 1. 前提条件
```bash
# AWS CLI設定
aws configure

# Python環境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows
```

### 2. 依存関係インストール
```bash
make install
# または
pip install -r requirements.txt
```

### 3. 環境変数設定
```bash
cp .env.example .env
# .envファイルを編集して実際の値を設定
```

### 4. インフラストラクチャデプロイ
```bash
# 全体デプロイ
make deploy

# または個別デプロイ
make tf-init
make tf-apply
make cfn-validate
```

## テスト実行

### 全テスト実行
```bash
make test
```

### 特定テスト実行
```bash
# 単体テストのみ
pytest tests/test_lambda_function.py::TestLambdaHandler -v

# 統合テストのみ
pytest tests/test_lambda_function.py::TestMotoIntegration -v

# 特定の関数テスト
pytest tests/test_lambda_function.py::TestFetchDatabaseData::test_fetch_database_data_success -v
```

### テストカバレッジ
```bash
pytest --cov=scripts tests/
```

## 開発ワークフロー

### 1. コード品質チェック
```bash
# リンティング
make lint

# フォーマット
make format
```

### 2. テスト駆動開発
```bash
# テスト作成
# tests/test_new_feature.py

# テスト実行
pytest tests/test_new_feature.py -v

# 実装
# scripts/new_feature.py

# 再テスト
pytest tests/test_new_feature.py -v
```

### 3. デプロイ前チェック
```bash
# CloudFormationテンプレート検証
make cfn-validate

# Terraformプラン確認
make tf-plan

# テスト実行
make test
```

## トラブルシューティング

### よくある問題

#### 1. IAMトークン認証エラー
```
psycopg2.OperationalError: FATAL: password authentication failed
```

**解決方法:**
- IAMユーザーにRDS接続権限があることを確認
- PostgreSQLでIAMユーザーが作成されていることを確認
- トークンの有効期限（15分）を確認

#### 2. VPC接続エラー
```
Lambda function timeout
```

**解決方法:**
- セキュリティグループの設定確認
- サブネットのルートテーブル確認
- NATゲートウェイの設定確認（プライベートサブネットの場合）

#### 3. Secrets Manager アクセスエラー
```
AccessDenied: User is not authorized to perform: secretsmanager:GetSecretValue
```

**解決方法:**
- Lambda実行ロールにSecrets Manager権限を追加
- シークレットのリソースポリシー確認

### デバッグ方法

#### 1. CloudWatch Logs確認
```bash
aws logs tail /aws/lambda/aurora-mock-testing-dev-data-processor --follow
```

#### 2. ローカルテスト
```bash
# 環境変数設定
export AURORA_SECRET_ARN="test-arn"
export API_URL="http://localhost:5000"

# テスト実行
python -m pytest tests/ -v -s
```

#### 3. モック確認
```python
# テスト内でモックの呼び出し確認
mock_secrets_client.get_secret_value.assert_called_once_with(
    SecretId='expected-secret-arn'
)
```

## パフォーマンス考慮事項

### Lambda最適化
- メモリサイズ: 256MB（調整可能）
- タイムアウト: 30秒
- 同時実行数制限の設定

### Aurora Serverless最適化
- 最小/最大ACU設定の調整
- 接続プールの使用
- クエリ最適化

### ECS最適化
- CPU/メモリ設定の調整
- ヘルスチェック設定
- オートスケーリング設定

## セキュリティベストプラクティス

### 1. 最小権限の原則
- 各サービスに必要最小限の権限のみ付与
- リソースベースのポリシー使用

### 2. 暗号化
- Aurora: 保存時暗号化有効
- Secrets Manager: デフォルト暗号化
- 通信: TLS/SSL使用

### 3. ネットワークセキュリティ
- プライベートサブネット使用
- セキュリティグループによる制限
- NACLによる追加制御

### 4. 監査とログ
- CloudTrail有効化
- CloudWatch Logs保存
- VPCフローログ有効化

## 運用・監視

### CloudWatch メトリクス
- Lambda: 実行時間、エラー率、同時実行数
- Aurora: CPU使用率、接続数、ACU使用量
- ECS: CPU/メモリ使用率、タスク数

### アラート設定
```bash
# Lambda エラー率アラート
aws cloudwatch put-metric-alarm \
  --alarm-name "Lambda-ErrorRate" \
  --alarm-description "Lambda error rate > 5%" \
  --metric-name "ErrorRate" \
  --namespace "AWS/Lambda" \
  --statistic "Average" \
  --period 300 \
  --threshold 5.0 \
  --comparison-operator "GreaterThanThreshold"
```

### バックアップ戦略
- Aurora: 自動バックアップ7日間保持
- Secrets Manager: バージョン管理有効
- Lambda: コードのGit管理

## 今後の拡張予定

### 機能拡張
- [ ] マルチAZ配置
- [ ] 読み取りレプリカ追加
- [ ] API Gateway統合
- [ ] Cognito認証追加

### 監視強化
- [ ] X-Ray トレーシング
- [ ] カスタムメトリクス
- [ ] ダッシュボード作成

### セキュリティ強化
- [ ] WAF追加
- [ ] Secrets Manager自動ローテーション
- [ ] VPC Endpoint使用

## 参考資料

- [AWS Aurora Serverless v2](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html)
- [RDS IAM Database Authentication](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.html)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [moto Documentation](https://docs.getmoto.org/en/latest/)
- [pytest Documentation](https://docs.pytest.org/)