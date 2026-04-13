# インフラストラクチャ図作成タスク

このドキュメントは、アーキテクチャ図が不足しているディレクトリと、その作成手順を記載しています。

## テンプレートファイル

新しい図を作成する際は、以下のテンプレートを使用してください：

- **AWS構成**: `src/aws-template.drawio`
- **OCI構成**: `src/oci-template.drawio`

## 図の作成手順

1. 対象ディレクトリの Terraform/CloudFormation ファイルを確認
2. 作成されるリソースと接続関係を把握
3. テンプレートファイルを開く（Draw.io Desktop または https://app.diagrams.net/）
4. 新しいファイルとして `<directory>/src/architecture.drawio` に保存
5. すべてのリソースとその接続を図示
6. ラベルと説明を日本語で記載
7. GitHub にコミット後、自動的に SVG ファイルが生成される（`.github/workflows/drawio-to-svg.yml`）

## 優先度1: コアインフラストラクチャ（図が必要）

### 040.network-connectivity-checker

**状態**: 図なし  
**種別**: マルチクラウド（AWS/Azure/GCP）  
**リソース**:
- AWS: VPC, Subnet, Security Group, EC2, RDS
- Azure: VNet, NSG, VM
- GCP: VPC, Firewall, VM, Cloud Run, Cloud SQL

**作成する図**: 各クラウドプロバイダーのリソースを別々のセクションに配置し、それぞれのネットワーク構成を示す

### 028.oci-bucket-tfstate

**状態**: 図なし  
**種別**: OCI Object Storage  
**リソース**:
- Object Storage Bucket
- Namespace

**作成する図**: シンプルな OCI Object Storage の構成図（Terraform State 管理用途を明示）

### 029.oci-cost-alert

**状態**: 図なし  
**種別**: OCI Budget/Notification  
**リソース**:
- Budget
- Budget Alert Rule
- Notification Topic
- Email Subscription

**作成する図**: 予算監視とアラート通知のフロー図

## 優先度2: 要確認ディレクトリ

以下のディレクトリは、インフラストラクチャコードを含んでいるため、図の有無を確認する必要があります：

- **008.ami,ec2**: AMI 作成と EC2 インスタンス構成
- **009.ami,windows_managed_instance**: Windows AMI 作成と管理インスタンス
- **014.bedrock-webcrawler**: Bedrock + OpenSearch + Lambda 構成
- **021.slack-lambda-mcp-server**: Slack + Lambda + OpenSearch + DynamoDB 構成
- **022.amazon_q_developer_in_chat_applications_by_slack**: Amazon Q Developer Slack 連携
- **023.bedrock-rag-agent-in-slack**: Bedrock RAG エージェント Slack 連携
- **033.apigateway-openapi-cognito-auth**: API Gateway + OpenAPI + Cognito 認証
- **036.scp-owner-tag-enforcement**: SCP 所有者タグ強制
- **038.lambda-layer-test**: Lambda Layer テスト
- **039.step-functions-nested-state-machine**: Step Functions ネストされたステートマシン

## README.md 更新タスク

図を作成した後、各ディレクトリの README.md に以下の参照を追加してください：

```markdown
![アーキテクチャ図](src/architecture.svg)
```

または

```markdown
![構成図](src/architecture.svg)
```

## 注意事項

- 図は日本語でラベルと説明を記載する
- AWS 2025 アイコンまたは OCI アイコンを使用する
- すべてのリソースとその接続関係を含める
- 図は実際のインフラストラクチャ構成を正確に反映する
- SVG ファイルは GitHub Actions ワークフローで自動生成される

## 進捗管理

- [ ] 040.network-connectivity-checker
- [ ] 028.oci-bucket-tfstate
- [ ] 029.oci-cost-alert
