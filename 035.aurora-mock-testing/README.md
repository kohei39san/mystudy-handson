# Aurora Mock Testing Project

このプロジェクトは、Aurora PostgreSQL、Secrets Manager、ECS、Lambdaを使用したシステムのモックテストを実装します。

## 構成

### CloudFormation リソース
- Aurora Serverless (PostgreSQL)
- Secrets Manager (Auroraエンドポイント情報)
- ECS (Flask REST API)
- Lambda (Python - データアクセス層)

### Terraform リソース
- IAMトークン認証用PostgreSQLユーザ

### テスト
- Lambda Python コードの単体テスト
- moto を使用したboto3.clientのモック
- unittest.mock を使用したpsycopg2のモック
- pytest monkeypatch を使用した環境変数のモック

## ディレクトリ構成

```
035.aurora-mock-testing/
├── README.md                 # このファイル
├── main.tf                   # Terraform メイン設定
├── variables.tf              # Terraform 変数定義
├── outputs.tf                # Terraform 出力定義
├── provider.tf               # Terraform プロバイダー設定
├── cfn/                      # CloudFormation テンプレート
│   ├── aurora.yaml
│   ├── secrets-manager.yaml
│   ├── ecs.yaml
│   └── lambda.yaml
├── scripts/                  # スクリプトファイル
│   ├── deploy.sh
│   └── lambda_function.py
└── tests/                    # 単体テストファイル
    ├── test_lambda_function.py
    └── conftest.py
```

## 技術仕様

- リージョン: ap-northeast-1
- Python 3.9+
- boto3
- psycopg2
- Flask
- pytest
- moto

## デプロイ手順

1. Terraform でIAMトークン認証を設定
2. CloudFormation でAWSリソースをデプロイ
3. テストスクリプトを実行

## テスト実行

```bash
cd tests/
pytest test_lambda_function.py -v
```