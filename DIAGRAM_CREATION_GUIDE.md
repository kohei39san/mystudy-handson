# インフラストラクチャ図作成ガイド

このドキュメントは、以下のディレクトリのインフラストラクチャ図を作成するためのガイドです。

## テンプレート

以下のテンプレートファイルを参照してください：
- **AWS構成**: `src/aws-template.drawio`
- **OCI構成**: `src/oci-template.drawio`

## 作成が必要な図（13ディレクトリ）

### AWS Terraform構成（8ディレクトリ）

#### 1. 008.ami,ec2
**ファイル名**: `008.ami,ec2/src/architecture.drawio`

**リソース**:
- VPC (10.0.0.0/16)
- Public Subnet (10.0.0.0/24)
- Internet Gateway
- Route Table
- Security Group (SSH)
- EC2 Instance
- Network Interface
- IAM Role (SSM管理用)
- IAM Instance Profile
- Key Pair
- AMI (作成)
- AMI Copy (大阪リージョン)
- Lambda Function (CloudFormation経由)

**接続**:
- VPC → Subnet
- Subnet → Internet Gateway
- EC2 → Network Interface → Subnet
- EC2 → Security Group
- EC2 → IAM Instance Profile → IAM Role
- EC2 → AMI作成
- AMI → AMI Copy (リージョン間)
- Lambda → AMI作成プロセス

---

#### 2. 009.ami,windows_managed_instance
**ファイル名**: `009.ami,windows_managed_instance/src/architecture.drawio`

**リソース**:
- VPC (10.0.0.0/16)
- Public Subnet (10.0.0.0/24)
- Internet Gateway
- Route Table
- Security Group (RDP)
- Windows EC2 Instance
- IAM Role (SSM管理用)
- IAM Instance Profile
- Key Pair
- AMI (Windows)
- Systems Manager
- CloudWatch Agent
- Zabbix Agent

---

#### 3. 010.ec2-linux-latest-eice
**ファイル名**: `010.ec2-linux-latest-eice/src/architecture.drawio`

**リソース**:
- VPC (10.0.0.0/16)
- Public Subnet (10.0.0.0/24)
- Private Subnet (10.0.1.0/24)
- Internet Gateway
- NAT Gateway
- Route Tables (Public/Private)
- Security Groups (EICE用、EC2用)
- EC2 Instance (Private Subnet)
- EC2 Instance Connect Endpoint
- IAM Role (SSM管理用)
- IAM Instance Profile

**接続**:
- Private Subnet → NAT Gateway → Internet Gateway
- EC2 Instance Connect Endpoint → EC2 Instance
- ユーザー → EICE → EC2 (プライベート)

---

#### 4. 014.bedrock-webcrawler
**ファイル名**: `014.bedrock-webcrawler/src/architecture.drawio`

**リソース**:
- Amazon Bedrock (Titan Embed Text v2)
- OpenSearch Domain (ベクトルDB)
- Lambda Function (Crawler)
- EventBridge Scheduler
- IAM Roles (Lambda, Bedrock, OpenSearch)
- CloudFormation Stack

**接続**:
- EventBridge → Lambda (定期実行)
- Lambda → Bedrock (モデル呼び出し)
- Bedrock → OpenSearch (ベクトル保存)

---

#### 5. 021.slack-lambda-mcp-server
**ファイル名**: `021.slack-lambda-mcp-server/src/architecture.drawio`

**リソース**:
- Slack App
- Slack Receiver Lambda
- SNS Topic
- MCP Server Lambda
- DynamoDB Table
- Amazon Bedrock Knowledge Base
- S3 Bucket
- GitHub Sync Lambda
- EventBridge Scheduler
- OpenSearch (マネージド)

**接続**:
- Slack → Slack Receiver Lambda → SNS → MCP Server Lambda
- MCP Server Lambda ↔ DynamoDB (キャッシュ)
- MCP Server Lambda → Bedrock KB → OpenSearch
- EventBridge → GitHub Sync Lambda → S3
- S3 → Bedrock KB (データソース)

---

#### 6. 022.amazon_q_developer_in_chat_applications_by_slack
**ファイル名**: `022.amazon_q_developer_in_chat_applications_by_slack/src/architecture.drawio`

**リソース**:
- Slack Workspace
- Slack Channel
- AWS Chatbot SlackChannelConfiguration
- IAM Role
- IAM Policy (ReadOnlyAccess, AmazonQDeveloperAccess)
- Amazon Q Developer

**接続**:
- Slack Channel → AWS Chatbot
- AWS Chatbot → IAM Role → Amazon Q Developer

---

#### 7. 023.bedrock-rag-agent-in-slack
**ファイル名**: `023.bedrock-rag-agent-in-slack/src/architecture.drawio`

**リソース**:
- Slack Channel
- AWS Chatbot SlackChannelConfiguration
- IAM Role
- Bedrock Agent
- Bedrock Knowledge Base
- OpenSearch Cluster
- S3 Bucket
- Lambda Function (GitHub同期)
- EventBridge Scheduler
- GitHub Repository

**接続**:
- Slack → AWS Chatbot → Bedrock Agent
- Bedrock Agent → Bedrock KB → OpenSearch
- EventBridge → Lambda → GitHub → S3
- S3 → Bedrock KB (データソース)

---

#### 8. 039.step-functions-nested-state-machine
**ファイル名**: `039.step-functions-nested-state-machine/src/architecture.drawio`

**リソース**:
- Parent State Machine
- Child State Machine
- Parent Lambda Function
- Child Lambda Function
- Child Output Filter Lambda
- IAM Roles (Step Functions, Lambda)
- CloudWatch Logs

**接続**:
- Parent State Machine → Parent Lambda (前処理)
- Parent State Machine → Child State Machine (同期呼び出し)
- Child State Machine → Child Lambda (2回)
- Parent State Machine → Child Output Filter Lambda
- Parent State Machine → Parent Lambda (後処理)

---

### OCI Terraform構成（2ディレクトリ）

#### 9. 028.oci-bucket-tfstate
**ファイル名**: `028.oci-bucket-tfstate/src/architecture.drawio`

**リソース**:
- Compartment
- Object Storage Bucket
- Bucket (バージョニング有効)

---

#### 10. 029.oci-cost-alert
**ファイル名**: `029.oci-cost-alert/src/architecture.drawio`

**リソース**:
- Compartment
- Budget
- Budget Alert Rule
- Notification Topic
- Email Subscription

**接続**:
- Budget → Alert Rule → Notification Topic → Email

---

### CloudFormation構成（3ディレクトリ）

#### 11. 033.apigateway-openapi-cognito-auth
**ファイル名**: `033.apigateway-openapi-cognito-auth/src/architecture.drawio`

**リソース**:
- User
- Amazon Cognito User Pool
- Cognito User Groups (api-admins, api-users)
- API Gateway (REST API)
- Lambda Authorizer
- Backend Lambda Functions (login, refresh, revoke, backend)
- IAM Roles
- CloudWatch Logs

**接続**:
- User → Cognito (認証)
- User → API Gateway (リクエスト)
- API Gateway → Cognito Authorizer (トークン検証)
- API Gateway → Lambda Authorizer (ロール検証)
- API Gateway → Backend Lambda (処理)

---

#### 12. 036.scp-owner-tag-enforcement
**ファイル名**: `036.scp-owner-tag-enforcement/src/architecture.drawio`

**リソース**:
- AWS Organizations
- Organization Unit (OU)
- Service Control Policy (SCP)
- Tag Policy
- AWS Accounts (複数)
- リソース作成アクション (EC2, RDS, etc.)

**接続**:
- Organizations → OU → Accounts
- SCP → OU (Ownerタグ強制)
- Tag Policy → OU (タグ形式制御)
- Accounts → リソース作成 (タグ検証)

---

#### 13. 038.lambda-layer-test
**ファイル名**: `038.lambda-layer-test/src/architecture.drawio`

**リソース**:
- Lambda Function
- Lambda Layer (pydantic, psycopg2)
- S3 Bucket (Layer保存用)
- Docker (Layer作成環境)
- CloudFormation Stack

**接続**:
- Docker → Lambda Layer ZIP
- Layer ZIP → S3 Bucket
- Lambda Function → Lambda Layer

---

## 図作成手順

1. **Draw.io Desktopを起動**
2. **テンプレートを開く**
   - AWS: `src/aws-template.drawio`
   - OCI: `src/oci-template.drawio`
3. **新しい図を作成**
   - 各ディレクトリの `src/architecture.drawio` として保存
4. **リソースを配置**
   - 上記のリソースリストを参照
   - テンプレートのアイコンを使用
5. **接続を描画**
   - リソース間の関係を矢印で表現
6. **ラベルを追加**
   - 日本語でリソース名や説明を追加
7. **保存**
   - 各ディレクトリの `src/architecture.drawio` に保存

## 自動SVG生成

`.drawio` ファイルを保存してGitHubにプッシュすると、GitHub Actions ワークフロー (`.github/workflows/drawio-to-svg.yml`) が自動的に `.svg` ファイルを生成します。

## 参考

既存の図がある以下のディレクトリを参考にしてください：
- 001.ec2-ec2,ec2/src/architecture.drawio
- 015.eks/src/architecture.drawio
- 030.apigateway-cognito-lambda-payload/src/architecture.drawio
