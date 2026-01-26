[![CodeQL Advanced](https://github.com/kohei39san/mystudy-handson/actions/workflows/codeql.yml/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/codeql.yml)
[![Terraform linter and PR](https://github.com/kohei39san/mystudy-handson/actions/workflows/terraform-linter-pr.yml/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/terraform-linter-pr.yml)
[![Dependabot Updates](https://github.com/kohei39san/mystudy-handson/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/dependabot/dependabot-updates)
[![CloudFormation Linter](https://github.com/kohei39san/mystudy-handson/actions/workflows/cfn-lint.yml/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/cfn-lint.yml)
[![GitHub Actions Linter](https://github.com/kohei39san/mystudy-handson/actions/workflows/github-actions-linter-pr.yml/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/github-actions-linter-pr.yml)
[![Ansible Linter](https://github.com/kohei39san/mystudy-handson/actions/workflows/ansible-linter-pr.yml/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/ansible-linter-pr.yml)

# 概要

勉強で使った基盤はEC2とTerraformで作りました。
このリポジトリには、AWS、OCI、Kubernetesなどの様々なクラウドインフラストラクチャのサンプル構成が含まれています。
各ディレクトリには、対応するインフラストラクチャのTerraformコード、CloudFormationテンプレート、またはその他の設定ファイルが含まれています。

# フォルダ構成

## インフラストラクチャディレクトリ

各番号付きディレクトリには、特定のインフラストラクチャ構成が含まれています：

* **001-038**: 各種インフラストラクチャのサンプル構成
  * **AWS Terraform構成**:
    - **001.ec2-ec2,ec2**: EC2踏み台サーバーとプライベートサーバー構成
    - **002.ec2windows**: Windows EC2インスタンス構成
    - **003.minikube-opensearch,prometheus**: Minikube + OpenSearch + Prometheus構成
    - **004.RDS_instance**: RDSインスタンス構成
    - **005.RDS_cluster**: RDSクラスター構成
    - **006.windows_managed_instance**: Windows Systems Manager管理インスタンス
    - **007.managed-node-linux**: Linux Systems Manager管理インスタンス
    - **008.ami,ec2**: AMI作成とEC2インスタンス構成
    - **009.ami,windows_managed_instance**: Windows AMI作成と管理インスタンス
    - **010.ec2-linux-latest-eice**: EC2 Instance Connect Endpoint構成
    - **012.openhands-test**: OpenHands テスト用EC2構成
    - **014.bedrock-webcrawler**: Bedrock Webクローラー構成
    - **015.eks**: EKS（Kubernetes）クラスター構成
    - **017.redmine-test**: Redmine テスト環境構成
    - **018.send-game-info-to-discord**: ゲーム情報Discord通知Lambda
    - **019.lambda-rss-summary**: RSS要約Lambda関数
    - **020.aws-readonly-oidc**: AWS読み取り専用OIDC認証
    - **021.slack-lambda-mcp-server**: Slack Lambda MCP サーバー
    - **022.amazon_q_developer_in_chat_applications_by_slack**: Amazon Q Developer Slack連携
    - **023.bedrock-rag-agent-in-slack**: Bedrock RAGエージェント Slack連携
    - **030.apigateway-cognito-lambda-payload**: API Gateway + Cognito + Lambda構成
    - **035.aurora-mock-testing**: Aurora モックテスト環境
  * **OCI Terraform構成**:
    - **028.oci-bucket-tfstate**: Object Storage（Terraformステート管理用）
    - **029.oci-cost-alert**: Budget（コストアラート）
  * **CloudFormationテンプレート**:
    - **011.cfn**: EC2基本構成
    - **013.aws-github-oidc**: GitHub Actions OIDC認証
    - **031.rds-postgresql-ec2**: RDS PostgreSQL + EC2構成
    - **032.scp-ec2-tagging**: SCP（Service Control Policy）EC2タグ強制
    - **033.apigateway-openapi-cognito-auth**: API Gateway + OpenAPI + Cognito認証
    - **036.scp-owner-tag-enforcement**: SCP所有者タグ強制
    - **038.lambda-layer-test**: Lambda Layer テスト
  * **Ansible Playbook**:
    - **025.ansible-vpc-test**: VPC作成
    - **026.ansible-aws-ec2**: EC2インスタンス管理
  * **CDK（TypeScript）**:
    - **024.test-custom-blea-gov-base-ct**: BLEA（Baseline Environment on AWS）ガバナンスベース
  * **その他**:
    - **016.setup-mcp-with-vscode**: MCP（Model Context Protocol）VSCode設定
    - **027.test-drawio**: Draw.io テスト用ディレクトリ
    - **034.redmine-mcp-server**: Redmine MCP サーバー
    - **037.kubectl-proxy**: kubectl proxy設定

## アーキテクチャ図について

各インフラストラクチャディレクトリには、対応するアーキテクチャ図が含まれています：

* **図の場所**: `src/architecture.drawio`（Draw.io形式）
* **SVG出力**: `src/architecture.svg`（自動生成）
* **README参照**: `![Architecture Diagram](src/architecture.svg)`

### 図の作成について

新しいアーキテクチャ図を作成する際は、以下のテンプレートを参考にしてください：

* **AWS構成**: `src/aws-template.drawio`
* **OCI構成**: `src/oci-template.drawio`

これらのテンプレートには、各クラウドプロバイダーの標準的なアイコンとレイアウトが含まれています。

## ディレクトリ構成の詳細

### 番号付きディレクトリの命名規則

* **001-010**: 基本的なEC2、RDS構成
* **011-020**: CloudFormation、特殊構成
* **021-030**: Lambda、API Gateway、高度な構成
* **031-038**: 特殊用途、テスト構成

### 各ディレクトリの共通構造

```
XXX.directory-name/
├── *.tf                    # Terraform設定ファイル（Terraform構成の場合）
├── cfn/                    # CloudFormationテンプレート（CFN構成の場合）
├── scripts/                # デプロイ・設定スクリプト
├── src/
│   ├── architecture.drawio # アーキテクチャ図（Draw.io形式）
│   └── architecture.svg    # アーキテクチャ図（SVG形式、自動生成）
├── terraform.tfvars.example # Terraform変数設定例
└── README.md               # 構成説明書
```

## 共通ディレクトリ

* **scripts**: 検証で使用したスクリプトを格納しています
* **src**: テンプレートファイルやその他の共通リソースを格納しています
  * `aws-template.drawio`: AWSアーキテクチャ図のテンプレート
  * `oci-template.drawio`: OCIアーキテクチャ図のテンプレート
* **wsl-old**: 過去WSL環境で使用したソースファイルを格納しています

各インフラストラクチャディレクトリには、対応するアーキテクチャ図（`src/architecture.drawio`）とREADME.mdファイルが含まれています。

# 使い方

1. リポジトリをクローンします。
2. AWS CLIを使うための認証の設定ができていることを確認します。

* PowerShellにてSSO認証を行う場合には以下のような設定ファイルを作成する

```conf:C:\Users\user\.aws\config
[profile default]
sso_start_url = <sso-start-url>
sso_region = <sso-region>
sso_account_id = <sso-account-id>
sso_role_name = <sso-account-id>
region = <region>
output = json
```

3. Terraform CLIにてデプロイします。パラメータは適宜Overrideなどで変更してください。

* PowerShellの場合の例(defaultプロファイルを使用)

```
# cd mystudy-handson\001.ec2-ec2,ec2
# PowerShell -ExecutionPolicy RemoteSigned '..\scripts\aws-cli-source.ps1 default'
# terraform init
# terraform plan
# terraform apply
```

# GitHub Actionsによる実行方法

## 週次README更新ワークフロー

このリポジトリには、週次でREADME.mdファイルの最新化を行うためのGitHub Actionsワークフローが含まれています。

### 機能概要

- 毎週月曜日の午前9時(UTC)に自動実行されます
- リポジトリ内のREADME.mdファイルを最新化するためのIssueを作成します
- 作成されたIssueには「Amazon Q development agent」ラベルが自動的に付与されます
- Amazon Qがラベルを検知し、README.mdの更新作業を自動的に開始します

### 設定方法

1. リポジトリの環境変数に`README_UPDATE_PROMPT`を設定することで、カスタムプロンプトを指定できます
2. 環境変数が設定されていない場合は、デフォルトのプロンプトが使用されます

### 手動実行

1. GitHubのActionsタブから「Weekly README Update」ワークフローを選択します
2. 「Run workflow」をクリックして手動で実行することもできます

## GitHub Actions YAMLファイルのLinter

このリポジトリには、GitHub ActionsのYAMLファイルを自動的にlintするためのワークフローが含まれています。

### 機能概要

- リポジトリ内のGitHub Actions YAMLファイル（`.github/workflows/*.yml`）の構文チェックを行います
- すべてのブランチへのプッシュ時に自動的に実行されます
- GitHub Actions YAMLファイル以外はlintの対象外です

### 使用されているツール

- [github/super-linter](https://github.com/github/super-linter): GitHubが提供する多言語対応のlintツール
  - YAML構文チェック
  - GitHub Actionsワークフロー構文チェック

### 注意事項

- このlinterはGitHub Actions YAMLファイルのみを対象としています
- 他のYAMLファイルはチェック対象外です

## 所有する別リポジトリへプッシュするワークフロー

このリポジトリには、コンテンツを別のリポジトリにプッシュするためのGitHub Actionsワークフローが含まれています。

### 機能概要

- メインブランチの内容を指定した別リポジトリにプッシュします
- プッシュ先リポジトリに新しいブランチを作成します
- プッシュ後、プッシュ先リポジトリのmainブランチに対するプルリクエストを自動作成します
- セキュリティのため、プッシュ先リポジトリは同じ所有者のリポジトリに限定されます

### 必要な設定

1. GitHub Secretsに以下の値を設定してください：
   - `TARGET_REPO_PAT`: プッシュ先リポジトリにアクセスするためのPersonal Access Token
   - `TARGET_REPO`: プッシュ先リポジトリ名（例: `owner/repo-name`）

### 使用方法

1. GitHubのActionsタブから「Push to Another Repository」ワークフローを選択します
2. 「Run workflow」をクリックし、以下の情報を入力します：
   - `Branch name to create in target repository`: 作成するブランチ名
   - `Commit message`: コミットメッセージ
   - `Pull request title`: プルリクエストのタイトル
   - `Pull request body`: プルリクエストの説明文
3. 「Run workflow」をクリックして実行を開始します

### 注意事項

- プッシュ先リポジトリは同じGitHubアカウント/組織が所有している必要があります
- 適切な権限を持つPersonal Access Tokenが必要です（repo権限を推奨）
- ワークフローは手動実行のみ可能です

## 前提条件

GitHub Actionsを使用するには、先にAWS側でOIDC認証のための設定が必要です。以下の手順で設定してください：

1. `013.aws-github-oidc/template.yaml`のCloudFormationテンプレートをデプロイします。
   * このテンプレートは以下のリソースを作成します：
     - GitHub Actions用のOIDCプロバイダー
     - GitHub Actionsが利用するIAMロール（PowerUserAccess権限付き）
   * デプロイ時にパラメータ`GitHubRepository`の指定が必要です
     - 形式: `repo:ユーザー名/リポジトリ名:ref:refs/heads/ブランチ名`
     - 例: `repo:example/mystudy-handson:ref:refs/heads/main`
     - 例: `repo:example/mystudy-handson:ref:refs/heads/*`

```powershell
> cd .\scripts\013.aws-github-oidc\
> PowerShell -ExecutionPolicy RemoteSigned './create-aws-oidc-provider.ps1 <stack-name> "組織名/リポジトリ名"'
```

`組織名/リポジトリ名` は、あなたのGitHubリポジトリの情報に置き換えてください。
例：`repo:<GitHub username>/<GitHub repository name>:ref:refs/heads/<branch name>`

2. デプロイ完了後、GitHub CLIをインストールし、`gh auth login`で認証を完了してください。

3. リポジトリの設定スクリプトを参考にGitHub Actions用の各種設定を行います：
```bat
scripts\setup-repository-for-github-actions.ps1
```
このスクリプトは以下の設定を行います：
* GitHub Actionsの権限設定
* 必要なSecrets（GEMINI_API_KEY, LLM_API_KEY, LLM_BASE_URL, PAT_TOKEN, PAT_USERNAME）の設定
* 必要なVariables（LLM_MODEL）の設定

## 実行手順

リポジトリにはTerraformを実行するためのGitHub Actionsワークフローが用意されています。
以下の手順で実行できます：

1. GitHubのActionsタブから「Terraform Apply Manual Test」ワークフローを選択します。

2. 「Run workflow」をクリックし、以下の情報を入力します：
   * `Directory number`: 実行するTerraformディレクトリの番号
     * 例: `001` (001.ec2-ec2,ec2ディレクトリを指定する場合)

注: ワークフローは実行時に選択されているブランチ上で実行されます。

3. 「Run workflow」をクリックして実行を開始します。

ワークフローは以下の順序で実行されます：
1. 現在のブランチをチェックアウト
2. 指定された番号のディレクトリを特定
3. terraform init
4. terraform plan
5. terraform apply
6. terraform destroy

注意事項：
* initまたはplanが失敗した場合、以降の処理は実行されません
* applyが失敗した場合でもdestroyは実行されます（ただしワークフロー自体は失敗として終了）
* 手動実行のみ可能です
