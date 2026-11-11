# Bedrock MCP Terraform

API GatewayからAgentCore Runtimeを呼び出し、AgentCore Gateway経由で公式GitHub MCP Serverを利用するための最小構成です。

## 構成

```text
Client (IAM/SigV4) -> API Gateway HTTP API -> Lambda adapter -> AgentCore Runtime -> AgentCore Gateway -> GitHub MCP Server (remote HTTPS)
```

MCPプロトコルのクライアント／サーバーは実装しません。LambdaはAgentCore Runtimeの`InvokeAgentRuntime` APIをboto3で呼び出すだけです。Lambda内にSigV4署名ロジックや長期アクセスキーは実装しません。

## 前提

- Terraform 1.6以上
- AWS provider 6.x
- AWS認証情報
- AWS provider 6.xで管理可能なAgentCore resourceの対応状況
- Docker daemonとDocker provider
- AgentCore Runtimeのコンテナイメージ定義
- Dockerまたは公式AgentCore CLIで生成したContainerプロジェクト
- GitHub OAuth AppのClient IDとClient Secret
- AgentCore Runtime側で設定するモデル、Harnessまたはエージェント、Gateway/MCPツール
- AgentCore Gateway側で設定する公式GitHub MCP ServerとGitHub OAuthまたはGitHub App認証

AgentCore Runtime、AgentCore Gateway、Gateway target、Runtime/Gateway用IAMロール、GitHub OAuth providerはAWS provider 6.xでTerraform管理します。`agentcore_runtime.tf`、`agentcore_gateway.tf`、`agentcore_targets.tf`、`github_oauth.tf`、`iam.tf`が実装済みです。provider schema、リージョン対応、作成・更新・削除の挙動は`terraform validate`と検証用AWSアカウントで確認します。

AgentCore RuntimeはTerraformで作成し、`agentcore_runtime_arn` outputをLambdaアダプターとIAMポリシーへ自動的に渡します。Runtime ARNを手入力するフォールバックは使用しません。

`agent_image_tag`を使って、TerraformがECRリポジトリ作成、Docker image build、ECR push、AgentCore RuntimeへのURI設定まで実行します。Terraformを実行する端末ではDocker daemonが起動している必要があります。

## Containerエージェント

このディレクトリには、公式AgentCore CLIのContainer build方針に合わせた最小テンプレートを配置しています。

```text
045.bedrock-mcp-terraform/
	Dockerfile
	requirements-agent.txt
	  agentcore_app/
		main.py
```

`agentcore_app/main.py`はAgentCore Runtimeのentrypointとして`prompt`を受け取り、`AGENTCORE_GATEWAY_URL`で指定されたAgentCore GatewayからGitHub MCP Serverのツール一覧を取得してStrands Agentへ渡します。GitHub OAuth情報はコンテナへ渡さず、Gateway側で管理します。

### Dockerイメージのビルドとpush

Docker providerがAWS ECR認証トークンを取得し、次の処理をTerraformから実行します。

```text
aws_ecr_repository
	|
	v
docker_image (Dockerfileからbuild)
	|
	v
docker_registry_image (ECRへpush)
	|
	v
aws_bedrockagentcore_agent_runtime
```

通常の実行手順:

```powershell
terraform init
terraform validate
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

`terraform destroy`では、ECRイメージを保持するため`docker_registry_image.keep_remotely = true`を設定しています。ECRリポジトリを削除する場合は、イメージを先に手動削除するか、削除専用の明示的な手順を実施してください。

```powershell
terraform init
terraform validate
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## AgentCoreリソースのTerraform管理

次のファイルで、AWS providerを使ってAgentCoreリソースを管理します。

| Terraform resource | 管理対象 |
|---|---|
| `aws_bedrockagentcore_agent_runtime` | AgentCore Runtime |
| `aws_bedrockagentcore_gateway` | AgentCore Gateway |
| `aws_bedrockagentcore_gateway_target` | GitHub MCP Server target |
| `aws_iam_role.agentcore_runtime` | AgentCore Runtime実行ロール |
| `aws_iam_role.agentcore_gateway` | AgentCore Gateway実行ロール |
| `aws_bedrockagentcore_oauth2_credential_provider.github` | GitHub OAuth provider |

```text
045.bedrock-mcp-terraform/
	agentcore_runtime.tf
	agentcore_gateway.tf
	agentcore_targets.tf
```

検証項目:

- AWS providerのresource schemaとAWSリージョン対応
- 必須プロパティとTerraform schema
- create/update/deleteおよびread-after-create
- 非同期operationの完了待ち
- Runtime ARN、Gateway ARN、Gateway endpointのTerraform output
- APIアダプターへのRuntime ARN受け渡し

`aws_bedrockagentcore_gateway_target`とGitHub OAuth providerはAWS providerで管理します。OAuth Client SecretはTerraform stateに含まれる可能性があるため、実値を`terraform.tfvars.example`へ記載せず、環境変数やCI/CDのsecretから`TF_VAR_github_oauth_client_secret`として渡してください。

## デプロイ

```powershell
terraform init
terraform fmt -check
terraform validate
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

Runtime、Gateway、Gateway targetは`terraform.tfvars`の設定から作成され、Runtime ARNはTerraform resourceのoutputからLambdaへ渡されます。

`api_authorizer_type`の初期値は`AWS_IAM`です。未認証アクセスを許可しない構成を標準とします。ローカル検証で一時的に認証を外す場合だけ、明示的に`NONE`を指定してください。

## IAM署名付き呼び出し

```powershell
$env:API_INVOKE_URL = terraform output -raw api_invoke_url
$env:AWS_REGION = "us-east-1"
$env:PROMPT = "List the repositories I can access"
python .\scripts\client_invoke.py
```

`scripts/client_invoke.py`はboto3の認証情報チェーン（IAM Identity Center、AWS CLIプロファイル等）を利用して、API GatewayへSigV4署名を付けます。AWSアクセスキーをソースコードへ埋め込まないでください。応答は非ストリーミングJSONとして受け取ります。

## 削除

```powershell
terraform destroy -var-file=terraform.tfvars
```

## 単体テスト

Lambdaアダプターの単体テストはAgentCore Runtimeへ接続せず、AWS SDKクライアントをモックして実行します。

```powershell
python -m pytest tests/test_api_adapter.py -q
```

## 注意

- API Gateway、Lambda、CloudWatch Logs、IAMはこのディレクトリで管理します。
- Runtime用のエージェントコードは`agentcore_app/`に配置し、API Gateway用コードとは分離します。
- Lambda実装は`scripts/api_adapter.py`、ローカル呼び出しサンプルは`scripts/client_invoke.py`に配置します。
- AgentCore Runtime/Gateway/Gateway targetはAWS providerでTerraform管理します。
- Runtime/Gateway用IAMロールとGitHub OAuth providerもAWS providerでTerraform管理します。
- `github_oauth_client_secret`の実値をGit管理対象ファイルへ記載しないでください。
- AgentCore Gatewayと公式GitHub MCP ServerのOAuth/GitHub App設定は、Gateway側の設定手順で管理します。
- API GatewayのIAM認証はTerraformで管理し、クライアントには`execute-api:Invoke`だけを許可します。
- VPC、サブネット、NAT Gateway、内部MCPサーバーは作成しません。
- Terraform stateには機密値を含めないでください。
