# インフラストラクチャ図とREADME監査レポート

## 監査日
2025年実施

## 監査の目的
- 各ディレクトリのREADME.mdがリソース構成を正確に反映しているか確認
- インフラストラクチャ図（architecture.drawio）の存在確認
- README.mdに図への参照が含まれているか確認

## 監査結果サマリー

### インフラストラクチャ図が存在し、README.mdが適切なディレクトリ
以下のディレクトリは図とREADME.mdが適切に整備されています：

1. **001.ec2-ec2,ec2** - EC2踏み台サーバーとプライベートサーバー構成 ✓
2. **002.ec2windows** - Windows EC2インスタンス構成 ✓
3. **003.minikube-opensearch,prometheus** - Minikube + OpenSearch + Prometheus構成 ✓
4. **004.RDS_instance** - RDSインスタンス構成 ✓
5. **005.RDS_cluster** - RDSクラスター構成 ✓
6. **006.windows_managed_instance** - Windows Systems Manager管理インスタンス ✓
7. **007.managed-node-linux** - Linux Systems Manager管理インスタンス ✓
8. **011.cfn** - CloudFormationサンプル構成 ✓
9. **012.openhands-test** - OpenHands テスト用EC2構成 ✓
10. **013.aws-github-oidc** - GitHub Actions OIDC認証 ✓
11. **015.eks** - EKS（Kubernetes）クラスター構成 ✓
12. **017.redmine-test** - Redmine テスト環境構成 ✓
13. **018.send-game-info-to-discord** - ゲーム情報Discord通知Lambda ✓
14. **019.lambda-rss-summary** - RSS要約Lambda関数 ✓
15. **020.aws-readonly-oidc** - AWS読み取り専用OIDC認証 ✓
16. **025.ansible-vpc-test** - Ansible VPC作成 ✓
17. **026.ansible-aws-ec2** - Ansible EC2インスタンス管理 ✓
18. **030.apigateway-cognito-lambda-payload** - API Gateway + Cognito + Lambda構成 ✓
19. **031.rds-postgresql-ec2** - RDS PostgreSQL + EC2構成 ✓
20. **032.scp-ec2-tagging** - SCP（Service Control Policy）EC2タグ強制 ✓
21. **035.aurora-mock-testing** - Aurora モックテスト環境 ✓

### インフラストラクチャ図の作成が必要なディレクトリ

#### AWS Terraform構成

1. **008.ami,ec2** - AMI作成とEC2インスタンス構成
   - リソース: Lambda, EC2, AMI, IAM, VPC
   - 優先度: 高

2. **009.ami,windows_managed_instance** - Windows AMI作成と管理インスタンス
   - リソース: EC2, AMI, Systems Manager, IAM
   - 優先度: 高

3. **010.ec2-linux-latest-eice** - EC2 Instance Connect Endpoint構成
   - リソース: EC2, VPC, EICE, IAM
   - 優先度: 高

4. **014.bedrock-webcrawler** - Bedrock Webクローラー構成
   - リソース: Bedrock, Lambda, OpenSearch, S3
   - 優先度: 高
   - 注記: CFNテンプレートも存在

5. **021.slack-lambda-mcp-server** - Slack Lambda MCP サーバー
   - リソース: Lambda, DynamoDB, OpenSearch, S3
   - 優先度: 高

6. **022.amazon_q_developer_in_chat_applications_by_slack** - Amazon Q Developer Slack連携
   - リソース: Lambda, API Gateway, Slack統合
   - 優先度: 中

7. **023.bedrock-rag-agent-in-slack** - Bedrock RAGエージェント Slack連携
   - リソース: Bedrock, Lambda, OpenSearch, S3
   - 優先度: 高

8. **039.step-functions-nested-state-machine** - ネストされたState Machine
   - リソース: Step Functions, Lambda
   - 優先度: 中

#### OCI Terraform構成

1. **028.oci-bucket-tfstate** - Object Storage（Terraformステート管理用）
   - リソース: Object Storage Bucket
   - 優先度: 中
   - テンプレート: src/oci-template.svg を参照

2. **029.oci-cost-alert** - Budget（コストアラート）
   - リソース: Budget, Notifications
   - 優先度: 中
   - テンプレート: src/oci-template.svg を参照

#### CloudFormation構成

1. **033.apigateway-openapi-cognito-auth** - API Gateway + OpenAPI + Cognito認証
   - リソース: API Gateway, Cognito, Lambda, OpenAPI
   - 優先度: 高

2. **036.scp-owner-tag-enforcement** - SCP所有者タグ強制
   - リソース: Organizations, SCP, Tag Policy
   - 優先度: 低

3. **038.lambda-layer-test** - Lambda Layer テスト
   - リソース: Lambda, Layer
   - 優先度: 低

### インフラストラクチャ図が不要なディレクトリ

以下のディレクトリはインフラストラクチャコードではないため、図は不要です：

1. **016.setup-mcp-with-vscode** - MCP（Model Context Protocol）VSCode設定
2. **024.test-custom-blea-gov-base-ct** - BLEA（CDKプロジェクト）
3. **027.test-drawio** - Draw.io テスト用ディレクトリ（テンプレート保存場所）
4. **034.redmine-mcp-server** - Redmine MCP サーバー（Pythonアプリケーション）
5. **037.kubectl-proxy** - kubectl proxy設定（設定ファイルのみ）

## 推奨事項

### 優先度：高
1. AWS Terraform構成で図が欠けているディレクトリの図を作成
   - 008, 009, 010, 014, 021, 023
   - テンプレート: `src/aws-template.drawio` を使用

### 優先度：中
1. OCI構成の図を作成（028, 029）
   - テンプレート: `src/oci-template.svg` を使用
2. 複雑なCloudFormation構成の図を作成（033）
3. README.mdで図への参照が欠けている箇所を追加

### 優先度：低
1. テスト用ディレクトリの図を作成（022, 038, 039）

## 注記
- すべてのインフラストラクチャ図は `src/architecture.drawio` として作成する必要があります
- SVGファイル（`src/architecture.svg`）はGitHub Actionsにより自動生成されます
- README.mdでの参照形式: `![Architecture Diagram](src/architecture.svg)`
