# RDS PostgreSQL with EC2 Access Setup

このプロジェクトは、AWS CloudFormationを使用してRDS PostgreSQLインスタンスとpsqlクライアントがインストールされたEC2インスタンスを構築します。EC2インスタンスはAWS Systems Managerを通じてSSH接続が可能で、RDSインスタンスにはIAMデータベース認証でアクセスできます。

## 構成概要

### アーキテクチャ
- **VPC**: 10.0.0.0/16 CIDR
- **パブリックサブネット**: EC2インスタンス用（10.0.1.0/24）
- **プライベートサブネット**: RDSインスタンス用（10.0.2.0/24, 10.0.3.0/24）
- **EC2インスタンス**: Amazon Linux 2023, t3.micro
- **RDSインスタンス**: PostgreSQL 15.4, db.t4g.micro
- **IAMロール**: Systems Manager接続とRDS IAM認証用

### コスト最適化
- 最小インスタンスタイプ（t3.micro, db.t4g.micro）を使用
- シングルAZ構成でRDSを配置
- バックアップ保持期間を0日に設定
- 暗号化ストレージを使用（セキュリティ要件）

## 前提条件

1. AWS CLIがインストールされ、適切な権限で設定されていること
2. 以下のAWS権限が必要：
   - CloudFormation操作権限
   - EC2、RDS、VPC、IAMリソースの作成・管理権限
   - Systems Manager操作権限

## デプロイ手順

### 0. ヘルプの確認

```bash
# scriptsディレクトリに移動
cd scripts

# 全スクリプトを実行可能にする
chmod +x *.sh

# 利用可能なコマンドを確認
./help.sh
```

### 1. CloudFormationスタックのデプロイ

```bash
# デプロイスクリプトを実行
./deploy.sh
```

デプロイ時にPostgreSQLのマスターパスワード（8文字以上）の入力が求められます。

### 2. 手動でのデプロイ（オプション）

```bash
# CloudFormationテンプレートを直接使用する場合
aws cloudformation deploy \
    --template-file cfn/rds-postgresql-ec2.yaml \
    --stack-name rds-postgresql-ec2-stack \
    --parameter-overrides DBPassword="YourSecurePassword123!" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ap-northeast-1
```

## 接続方法

### 1. AWS Systems ManagerでEC2に接続

```bash
# EC2インスタンスIDを取得
EC2_INSTANCE_ID=$(aws cloudformation describe-stacks \
    --stack-name rds-postgresql-ec2-stack \
    --region ap-northeast-1 \
    --query 'Stacks[0].Outputs[?OutputKey==`EC2InstanceId`].OutputValue' \
    --output text)

# Systems Managerセッションを開始
aws ssm start-session --target $EC2_INSTANCE_ID --region ap-northeast-1
```

### 2. EC2からRDS PostgreSQLに接続

EC2インスタンスに接続後、以下のスクリプトが利用可能です：

#### パスワード認証での接続
```bash
# 事前に作成されたスクリプトを使用
./connect-to-rds.sh
```

#### IAM認証での接続
```bash
# IAM認証を使用した接続
./connect-to-rds-iam.sh
```

**注意**: IAM認証を使用する前に、データベース内でIAMユーザーを作成する必要があります：

```sql
-- パスワード認証で接続後、以下のSQLを実行
CREATE USER postgres WITH LOGIN;
GRANT rds_iam TO postgres;
```

#### 手動での接続
```bash
# 環境変数を読み込み
source rds-env.sh

# パスワード認証
psql -h $RDS_ENDPOINT -p 5432 -U $DB_USER -d $DB_NAME

# IAM認証
TOKEN=$(aws rds generate-db-auth-token --hostname $RDS_ENDPOINT --port 5432 --username $DB_USER --region $AWS_REGION)
PGPASSWORD=$TOKEN psql -h $RDS_ENDPOINT -p 5432 -U $DB_USER -d $DB_NAME
```

## 管理コマンド

### テンプレートの検証

```bash
# テンプレート検証スクリプトを実行可能にする
chmod +x validate-template.sh

# CloudFormationテンプレートの構文を検証
./validate-template.sh
```

### スタック状態の確認

```bash
# 状態確認スクリプトを実行可能にする
chmod +x check-status.sh

# スタックとリソースの状態を確認
./check-status.sh
```

### 接続テスト（EC2インスタンス上で実行）

```bash
# 接続テストスクリプトを実行可能にする（EC2上で）
chmod +x test-connection.sh

# RDS接続の各種テストを実行
./test-connection.sh
```

### スタックの削除

```bash
# クリーンアップスクリプトを実行可能にする
chmod +x cleanup.sh

# スタックとすべてのリソースを削除
./cleanup.sh
```

## ファイル構成

```
031.rds-postgresql-ec2/
├── README.md                           # このファイル
├── cfn/
│   └── rds-postgresql-ec2.yaml        # CloudFormationテンプレート
└── scripts/
    ├── deploy.sh                       # デプロイスクリプト
    ├── cleanup.sh                      # クリーンアップスクリプト
    ├── check-status.sh                 # 状態確認スクリプト
    ├── validate-template.sh            # テンプレート検証スクリプト
    ├── test-connection.sh              # 接続テストスクリプト（EC2上で実行）
    └── help.sh                         # ヘルプ・使用方法表示スクリプト
```

## CloudFormationテンプレートの詳細

### パラメータ
- `DBUsername`: データベースのマスターユーザー名（デフォルト: postgres）
- `DBPassword`: データベースのマスターパスワード（8-128文字）
- `EnvironmentName`: リソース命名用の環境名（デフォルト: rds-postgresql-demo）

### 主要リソース
- **VPC**: カスタムVPCとサブネット
- **EC2インスタンス**: PostgreSQLクライアントがプリインストールされたAmazon Linux 2023
- **RDSインスタンス**: PostgreSQL 15.4データベース
- **セキュリティグループ**: EC2からRDSへのアクセスを許可
- **IAMロール**: Systems Manager接続とRDS IAM認証用

### 出力値
- VPC ID
- EC2インスタンスID
- RDSエンドポイント
- RDSポート
- データベース名
- データベースユーザー名
- Systems Manager接続コマンド
- PostgreSQL接続コマンド

## セキュリティ考慮事項

1. **ネットワークセキュリティ**
   - RDSインスタンスはプライベートサブネットに配置
   - セキュリティグループでEC2からRDSへのアクセスのみ許可

2. **認証**
   - RDSはパスワード認証とIAM認証の両方をサポート
   - EC2はSystems Managerを通じてキーペア不要でアクセス

3. **暗号化**
   - RDSストレージは暗号化を有効化
   - 転送中のデータはSSL/TLS暗号化

## トラブルシューティング

### よくある問題

1. **Systems Manager接続ができない**
   - EC2インスタンスが起動完了していることを確認
   - SSMエージェントが実行中であることを確認
   - IAMロールが正しく設定されていることを確認

2. **RDS接続ができない**
   - RDSインスタンスが「available」状態であることを確認
   - セキュリティグループの設定を確認
   - 接続文字列が正しいことを確認

3. **IAM認証が失敗する**
   - EC2のIAMロールにRDS接続権限があることを確認
   - RDSでIAMデータベース認証が有効になっていることを確認

### ログの確認

```bash
# EC2インスタンスのユーザーデータログを確認
sudo cat /var/log/cloud-init-output.log

# SSMエージェントのステータス確認
sudo systemctl status amazon-ssm-agent
```

## コスト見積もり

月額概算コスト（ap-northeast-1リージョン）：
- EC2 t3.micro: 約 $8.50/月
- RDS db.t4g.micro: 約 $13.00/月
- EBS gp2 20GB: 約 $2.40/月
- **合計**: 約 $24/月

※実際のコストは使用量や為替レートにより変動します。

## 注意事項

1. このテンプレートは開発・テスト環境向けです
2. 本番環境では以下の設定を検討してください：
   - Multi-AZ配置
   - バックアップ設定
   - より大きなインスタンスタイプ
   - 削除保護の有効化
3. 不要になったリソースは必ずクリーンアップしてください

## サポート

問題が発生した場合は、以下を確認してください：
1. AWS CloudFormationコンソールでスタックイベントを確認
2. EC2インスタンスのシステムログを確認
3. RDSインスタンスのログを確認