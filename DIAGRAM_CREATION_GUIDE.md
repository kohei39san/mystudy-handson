# アーキテクチャ図作成ガイド

このガイドは、各ディレクトリで欠けているインフラストラクチャ図を作成するための詳細な指示を提供します。

## テンプレートファイル

### AWS構成
- **テンプレートファイル**: `src/aws-template.drawio`
- **使用アイコン**: AWS Architecture Icons (2025)
- **保存場所**: 各ディレクトリの `src/architecture.drawio`

### OCI構成
- **テンプレートファイル**: `src/oci-template.svg`
- **使用アイコン**: Oracle Cloud Infrastructure Icons
- **保存場所**: 各ディレクトリの `src/architecture.drawio`

## 図作成が必要なディレクトリと含めるべきリソース

### 優先度: 高

#### 008.ami,ec2 - AMI作成とEC2インスタンス構成

**含めるべきリソース:**
1. **VPC** - 10.0.0.0/16
2. **パブリックサブネット** - 10.0.0.0/24
3. **EC2インスタンス** - AMI作成元のインスタンス
4. **AMIイメージ** - 作成されるカスタムAMI
5. **Lambda関数** - AMI作成をトリガーする関数
6. **IAMロール** - Lambda実行ロール
7. **キーペア** - SSH接続用
8. **セキュリティグループ** - SSH許可

**データフロー:**
- Lambda → EC2 AMI作成
- AMI → 新しいEC2インスタンスの起動

**参照ファイル:**
- `ami.tf` - AMI定義
- `lambda.tf` - Lambda関数
- `iam.tf` - IAMロール
- `network.tf` - VPC/サブネット

---

#### 009.ami,windows_managed_instance - Windows AMI作成と管理インスタンス

**含めるべきリソース:**
1. **VPC** - 10.0.0.0/16
2. **パブリックサブネット** 
3. **EC2インスタンス (Windows)** - AMI作成元
4. **AMIイメージ** - カスタムWindows AMI
5. **Systems Manager** - 管理インスタンス接続
6. **IAMロール** - SSM実行ロール
7. **キーペア** - RDP接続用
8. **セキュリティグループ** - RDP許可

**データフロー:**
- Systems Manager → Windows EC2管理
- EC2 → AMI作成
- スクリプト実行: CloudWatch Agent, Zabbix Agent

**参照ファイル:**
- `ami.tf` - AMI定義
- `iam.tf` - IAMロール
- `server.tf` - EC2インスタンス
- `scripts/` - インストールスクリプト

---

#### 010.ec2-linux-latest-eice - EC2 Instance Connect Endpoint構成

**含めるべきリソース:**
1. **VPC** - 10.0.0.0/16
2. **プライベートサブネット**
3. **EC2インスタンス (Linux)**
4. **EC2 Instance Connect Endpoint (EICE)**
5. **IAMロール** - EC2実行ロール
6. **セキュリティグループ** - EICE接続許可
7. **キーペア** (オプション)

**データフロー:**
- ユーザー → EICE → プライベートEC2
- SSHトンネル接続

**参照ファイル:**
- `eice.tf` - EICE定義
- `server.tf` - EC2インスタンス
- `network.tf` - VPC/サブネット

---

#### 014.bedrock-webcrawler - Bedrock Webクローラー構成

**含めるべきリソース:**
1. **Lambda関数** - Webクローラー
2. **Amazon Bedrock** - Knowledge Base
3. **OpenSearch Serverless** - ベクトルストア
4. **S3バケット** - データソース
5. **IAMロール** - Lambda/Bedrock実行ロール
6. **EventBridge** (オプション) - スケジュール実行

**データフロー:**
- Lambda → Webページクロール → S3保存
- S3 → Bedrock Knowledge Base → OpenSearch
- ユーザークエリ → Bedrock → OpenSearch検索

**参照ファイル:**
- `bedrock.tf` - Bedrock設定
- `lambda.tf` - Lambda関数
- `opensearch.tf` - OpenSearch設定

---

#### 021.slack-lambda-mcp-server - Slack Lambda MCP サーバー

**含めるべきリソース:**
1. **Lambda関数** (複数) - Slack受信、MCP処理
2. **API Gateway** - Slack Webhook受信
3. **DynamoDB** - 状態管理
4. **OpenSearch** - ドキュメント検索
5. **S3バケット** - ドキュメント保存
6. **IAMロール** - 各サービス実行ロール
7. **Slack App** (外部) - イベント送信元

**データフロー:**
- Slack → API Gateway → Lambda
- Lambda → DynamoDB (状態保存)
- Lambda → OpenSearch (検索)
- Lambda → S3 (ドキュメント取得)
- Lambda → Slack (応答)

**参照ファイル:**
- `lambda.tf` - Lambda関数
- `dynamodb.tf` - DynamoDB設定
- `opensearch.tf` - OpenSearch設定
- `s3.tf` - S3バケット

---

#### 023.bedrock-rag-agent-in-slack - Bedrock RAGエージェント Slack連携

**含めるべきリソース:**
1. **Lambda関数** - Slack統合
2. **Amazon Bedrock Agent** - RAGエージェント
3. **Bedrock Knowledge Base**
4. **OpenSearch Serverless** - ベクトルストア
5. **S3バケット** - ドキュメントソース
6. **API Gateway** - Slack Webhook
7. **IAMロール** - 各サービス実行ロール
8. **Slack App** (外部)

**データフロー:**
- Slack → API Gateway → Lambda
- Lambda → Bedrock Agent
- Bedrock Agent → Knowledge Base → OpenSearch
- S3 → Knowledge Base (ドキュメント同期)
- Lambda → Slack (応答)

**参照ファイル:**
- `modules/bedrock_stack/` - Bedrock設定
- `modules/lambda_stack/` - Lambda設定
- `modules/main_stack/` - メイン統合

---

### 優先度: 中

#### 028.oci-bucket-tfstate - Object Storage（Terraformステート管理用）

**含めるべきリソース:**
1. **Compartment** (OCI)
2. **Object Storage Bucket**
3. **バージョニング設定** (有効)
4. **アクセス制御** (NoPublicAccess)
5. **Terraform State** (概念図)

**データフロー:**
- Terraform CLI → Object Storage (state保存/読み込み)

**参照ファイル:**
- `main.tf` - バケット定義
- `outputs.tf` - 出力値

**使用テンプレート:** `src/oci-template.svg`

---

#### 029.oci-cost-alert - Budget（コストアラート）

**含めるべきリソース:**
1. **Compartment** (OCI)
2. **Budget** - 予算設定
3. **Budget Alert Rule** - アラートルール
4. **Notification Topic** - 通知トピック
5. **Email Subscription** - メール購読
6. **Email Address** (外部)

**データフロー:**
- OCI コスト監視 → Budget閾値チェック
- Alert Rule トリガー → Notification Topic
- Topic → Email Subscription → ユーザー

**参照ファイル:**
- `budget.tf` - 予算/アラート設定
- `outputs.tf` - 出力値

**使用テンプレート:** `src/oci-template.svg`

---

#### 033.apigateway-openapi-cognito-auth - API Gateway + OpenAPI + Cognito認証

CloudFormationテンプレートから以下を図示:
- API Gateway (OpenAPI仕様)
- Cognito User Pool
- Lambda Authorizer
- Backend Lambda関数
- OpenAPI定義ファイル

---

## 図作成後の確認事項

1. ✅ `src/architecture.drawio` が作成されている
2. ✅ README.mdに `![Architecture Diagram](src/architecture.svg)` が記載されている
3. ✅ GitHub Actionsにより `src/architecture.svg` が自動生成される
4. ✅ すべてのラベルが日本語で記述されている
5. ✅ リソース間の接続線が正しく描画されている
