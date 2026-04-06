# インフラストラクチャ図の状態レポート

## 概要

このドキュメントは、リポジトリ内の各インフラストラクチャディレクトリにおけるアーキテクチャ図の作成状況を記録しています。

## テンプレートファイル

新しい図を作成する際は、以下のテンプレートファイルを使用してください：
- **AWS構成**: `src/aws-template.drawio`
- **OCI構成**: `src/oci-template.drawio`

## 状態の凡例

- ✅ **完了**: アーキテクチャ図とREADME.mdが存在し、正しく参照されている
- ⚠️ **要作成**: インフラストラクチャコードは存在するが、図が未作成
- ℹ️ **不要**: インフラストラクチャコードが含まれていないため、図は不要

## AWS Terraform構成

| ディレクトリ | 状態 | 備考 |
|------------|------|------|
| 001.ec2-ec2,ec2 | ✅ | EC2踏み台サーバーとプライベートサーバー |
| 002.ec2windows | ✅ | Windows EC2インスタンス |
| 003.minikube-opensearch,prometheus | ✅ | Minikube + OpenSearch + Prometheus |
| 004.RDS_instance | ✅ | RDSインスタンス |
| 005.RDS_cluster | ✅ | RDSクラスター |
| 006.windows_managed_instance | ✅ | Windows Systems Manager管理インスタンス |
| 007.managed-node-linux | ✅ | Linux Systems Manager管理インスタンス |
| 008.ami,ec2 | ⚠️ | AMI作成とEC2インスタンス - 図を作成する必要があります |
| 009.ami,windows_managed_instance | ⚠️ | Windows AMI作成と管理インスタンス - 図を作成する必要があります |
| 010.ec2-linux-latest-eice | ⚠️ | EC2 Instance Connect Endpoint - 図を作成する必要があります |
| 012.openhands-test | ✅ | OpenHands テスト用EC2 |
| 014.bedrock-webcrawler | ⚠️ | Bedrock Webクローラー - 図を作成する必要があります |
| 015.eks | ✅ | EKS（Kubernetes）クラスター |
| 017.redmine-test | ✅ | Redmine テスト環境 |
| 018.send-game-info-to-discord | ✅ | ゲーム情報Discord通知Lambda |
| 019.lambda-rss-summary | ✅ | RSS要約Lambda関数 |
| 020.aws-readonly-oidc | ✅ | AWS読み取り専用OIDC認証 |
| 021.slack-lambda-mcp-server | ⚠️ | Slack Lambda MCPサーバー - 図を作成する必要があります |
| 022.amazon_q_developer_in_chat_applications_by_slack | ⚠️ | Amazon Q Developer Slack連携 - 図を作成する必要があります |
| 023.bedrock-rag-agent-in-slack | ⚠️ | Bedrock RAGエージェント Slack連携 - 図を作成する必要があります |
| 030.apigateway-cognito-lambda-payload | ✅ | API Gateway + Cognito + Lambda |
| 035.aurora-mock-testing | ✅ | Aurora モックテスト環境 |
| 039.step-functions-nested-state-machine | ⚠️ | Step Functions ネストされたステートマシン - 図を作成する必要があります |

## OCI Terraform構成

| ディレクトリ | 状態 | 備考 |
|------------|------|------|
| 028.oci-bucket-tfstate | ⚠️ | Object Storage（Terraformステート管理用） - 図を作成する必要があります |
| 029.oci-cost-alert | ⚠️ | Budget（コストアラート） - 図を作成する必要があります |

## CloudFormationテンプレート

| ディレクトリ | 状態 | 備考 |
|------------|------|------|
| 011.cfn | ✅ | EC2基本構成 |
| 013.aws-github-oidc | ✅ | GitHub Actions OIDC認証 |
| 031.rds-postgresql-ec2 | ✅ | RDS PostgreSQL + EC2 |
| 032.scp-ec2-tagging | ✅ | SCP（Service Control Policy）EC2タグ強制 |
| 033.apigateway-openapi-cognito-auth | ⚠️ | API Gateway + OpenAPI + Cognito認証 - 図を作成する必要があります |
| 036.scp-owner-tag-enforcement | ⚠️ | SCP所有者タグ強制 - 図を作成する必要があります |
| 038.lambda-layer-test | ⚠️ | Lambda Layer テスト - 図を作成する必要があります |

## Ansible Playbook

| ディレクトリ | 状態 | 備考 |
|------------|------|------|
| 025.ansible-vpc-test | ✅ | VPC作成 |
| 026.ansible-aws-ec2 | ✅ | EC2インスタンス管理 |

## その他のプロジェクト

| ディレクトリ | 状態 | 備考 |
|------------|------|------|
| 016.setup-mcp-with-vscode | ℹ️ | MCP（Model Context Protocol）VSCode設定 - インフラストラクチャなし |
| 024.test-custom-blea-gov-base-ct | ℹ️ | BLEA（Baseline Environment on AWS）ガバナンスベース - CDKプロジェクト |
| 027.test-drawio | ℹ️ | Draw.io テスト用ディレクトリ - テスト専用 |
| 034.redmine-mcp-server | ℹ️ | Redmine MCPサーバー - インフラストラクチャなし |
| 037.kubectl-proxy | ℹ️ | kubectl proxy設定 - ローカル設定のみ |

## 作成が必要な図のリスト

以下のディレクトリには、アーキテクチャ図を作成する必要があります：

### 優先度: 高（AWS Terraform構成）
1. **008.ami,ec2** - AMI作成プロセスとEC2インスタンスの関係を図示
2. **009.ami,windows_managed_instance** - Windows AMI作成とSystems Manager統合を図示
3. **010.ec2-linux-latest-eice** - EC2 Instance Connect Endpointの接続フローを図示
4. **014.bedrock-webcrawler** - Bedrock、Lambda、OpenSearchの統合を図示
5. **021.slack-lambda-mcp-server** - Slack、Lambda、MCPサーバーの統合を図示
6. **022.amazon_q_developer_in_chat_applications_by_slack** - Amazon Q DeveloperとSlackの統合を図示
7. **023.bedrock-rag-agent-in-slack** - Bedrock RAGエージェントとSlackの統合を図示
8. **039.step-functions-nested-state-machine** - Step Functionsのネストされたステートマシンを図示

### 優先度: 中（OCI構成）
9. **028.oci-bucket-tfstate** - OCI Object Storageの構成を図示
10. **029.oci-cost-alert** - OCI Budgetとアラート構成を図示

### 優先度: 低（CloudFormation）
11. **033.apigateway-openapi-cognito-auth** - API Gateway、OpenAPI、Cognito統合を図示
12. **036.scp-owner-tag-enforcement** - SCPポリシーの適用範囲を図示
13. **038.lambda-layer-test** - Lambda Layerの構造を図示

## 図作成時の注意事項

1. **テンプレートの使用**: 必ず`src/aws-template.drawio`または`src/oci-template.drawio`を基に作成してください
2. **ファイル配置**: 各ディレクトリの`src/`サブディレクトリに`architecture.drawio`として保存してください
3. **SVG生成**: GitHub Actionsワークフロー（`.github/workflows/drawio-to-svg.yml`）が自動的にSVGファイルを生成します
4. **日本語表記**: すべてのラベルと説明は日本語で記述してください
5. **README参照**: 各ディレクトリのREADME.mdに`![構成図](src/architecture.svg)`を追加してください

## 次のステップ

1. 上記の「作成が必要な図のリスト」に記載されたディレクトリの図を作成
2. 各ディレクトリのREADME.mdが最新のインフラストラクチャ構成を反映していることを確認
3. すべてのREADME.mdファイルに図への参照が含まれていることを確認
