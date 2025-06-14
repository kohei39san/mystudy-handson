# Bedrock Agent を使用した Slack チャットアプリケーション

## 概要

このプロジェクトは、Amazon Bedrock Agent を使用して Slack からチャットで応答できるシステムを構築するための CloudFormation スタックを提供します。ユーザーは Slack チャンネル内で質問を投げかけると、Bedrock Agent が回答を生成し、その場で返信します。

## アーキテクチャ

```mermaid
graph TD
    User[ユーザー] -->|質問| SlackChannel[Slack チャンネル]
    SlackChannel -->|メッセージ| SlackConfig[SlackChannelConfiguration]
    SlackConfig -->|リクエスト| IAMRole[IAM ロール]
    IAMRole -->|アクセス権限| BedrockAgent[Bedrock Agent]
    BedrockAgent -->|クエリ| BedrockKB[Bedrock ナレッジベース]
    BedrockKB -->|検索| OpenSearch[OpenSearch クラスター]
    OpenSearch -->|ベクトル検索| S3[S3 バケット]
    S3 -->|ドキュメント格納| Lambda[Lambda 関数]
    Lambda -->|ドキュメント同期| GitHub[GitHub リポジトリ]
    EventBridge[EventBridge スケジューラー] -->|定期実行| Lambda
    BedrockAgent -->|回答| SlackChannel
    
    classDef aws fill:#FF9900,stroke:#232F3E,color:#232F3E;
    classDef external fill:#1DB954,stroke:#0A8043,color:#fff;
    
    class BedrockAgent,BedrockKB,OpenSearch,S3,Lambda,IAMRole,SlackConfig,EventBridge aws;
    class User,SlackChannel,GitHub external;
```

このシステムは以下のコンポーネントで構成されています：

1. **Slack チャンネル設定**
   - Amazon Q Developer in Chat Applications の SlackChannelConfiguration を使用
   - Slack ワークスペースと特定のチャンネルを AWS サービスと連携

2. **IAM ロールとポリシー**
   - Slack チャンネル設定に紐づく IAM ロール
   - Bedrock Agent へのアクセス権限を持つポリシー

3. **Amazon Bedrock コンポーネント**
   - Bedrock Agent: ユーザーからの質問に応答するエージェント
   - Bedrock ナレッジベース: 情報源となるドキュメントを管理
   - Bedrock Agent Alias: エージェントのバージョン管理

4. **OpenSearch マネージドクラスター**
   - ベクトルデータベースとして機能
   - ドキュメントの埋め込みベクトルを保存し、類似検索を実行

5. **S3 バケット**
   - ナレッジベースのソースとなるドキュメントを保存
   - GitHub リポジトリから同期されたドキュメントを格納

6. **Lambda 関数**
   - 指定した GitHub リポジトリから S3 バケットにドキュメントを同期
   - GitHub Personal Access Token (PAT) を使用してリポジトリにアクセス

7. **EventBridge スケジューラー**
   - Lambda 関数を定期的に実行し、ドキュメントを最新の状態に保つ

## デプロイ方法

### 前提条件

- AWS CLI がインストールされ、適切に設定されていること
- Slack ワークスペースの管理者権限
- GitHub リポジトリへのアクセス権と Personal Access Token
- Terraform 1.0.0 以上がインストールされていること

### デプロイ手順

#### Lambda 関数のソースコードの準備

1. Lambda 関数のソースコードディレクトリを作成します
   ```bash
   mkdir -p lambda_source/github_to_s3_sync
   cp scripts/023.bedrock-rag-agent-in-slack/github_to_s3_sync.py lambda_source/github_to_s3_sync/
   cp scripts/023.bedrock-rag-agent-in-slack/requirements.txt lambda_source/github_to_s3_sync/
   ```

#### Terraform を使用したデプロイ

1. terraform.tfvars ファイルを作成し、必要なパラメータを設定します
   ```
   # terraform.tfvars の例
   aws_region          = "us-east-1"
   project_name        = "bedrock-slack-chat"
   slack_workspace_id  = "YOUR_WORKSPACE_ID"
   slack_channel_id    = "YOUR_CHANNEL_ID"
   slack_channel_name  = "YOUR_CHANNEL_NAME"
   github_repository_url = "https://github.com/yourusername/yourrepo"
   github_pat          = "YOUR_GITHUB_PAT"
   ```

2. Terraform を初期化し、デプロイを実行します
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

3. デプロイが完了すると、自動的に Lambda 関数が実行され、GitHub リポジトリから S3 バケットにドキュメントが同期されます。

#### CloudFormation を使用したデプロイ（従来の方法）

1. パラメータの準備
   ```
   # 必要なパラメータ
   - SlackWorkspaceId: Slack ワークスペースの ID
   - SlackChannelId: Slack チャンネルの ID
   - SlackChannelName: Slack チャンネルの名前
   - BedrockModelId: 使用する Bedrock モデルの ID
   - GitHubRepositoryUrl: ナレッジベースのソースとなる GitHub リポジトリの URL
   - GitHubPAT: GitHub Personal Access Token
   ```

2. CloudFormation スタックのデプロイ
   ```bash
   aws cloudformation deploy \
     --template-file template.yaml \
     --stack-name bedrock-slack-chat \
     --parameter-overrides \
       SlackWorkspaceId=YOUR_WORKSPACE_ID \
       SlackChannelId=YOUR_CHANNEL_ID \
       SlackChannelName=YOUR_CHANNEL_NAME \
       BedrockModelId=YOUR_MODEL_ID \
       GitHubRepositoryUrl=YOUR_REPO_URL \
       GitHubPAT=YOUR_PAT \
     --capabilities CAPABILITY_NAMED_IAM
   ```

3. Bedrock スタックのデプロイ
   ```bash
   aws cloudformation deploy \
     --template-file bedrock-template.yaml \
     --stack-name bedrock-agent-stack \
     --parameter-overrides \
       MainStackName=bedrock-slack-chat \
     --capabilities CAPABILITY_IAM
   ```

4. Lambda スタックのデプロイ
   ```bash
   aws cloudformation deploy \
     --template-file lambda-template.yaml \
     --stack-name bedrock-lambda-stack \
     --parameter-overrides \
       MainStackName=bedrock-slack-chat \
     --capabilities CAPABILITY_IAM
   ```

5. Lambda 関数を手動で実行して、GitHub リポジトリから S3 バケットにドキュメントを同期します
   ```bash
   aws lambda invoke \
     --function-name bedrock-slack-chat-github-to-s3-sync \
     --payload '{}' \
     /tmp/lambda_output.json
   ```

## 自動デプロイ後の処理

このプロジェクトには、Terraform を使用してデプロイした後に自動的に Lambda 関数を実行する機能が含まれています。この機能により、以下のメリットがあります：

1. **即時のデータ同期**：デプロイ直後に GitHub リポジトリから S3 バケットにドキュメントが同期されます
2. **手動操作の削減**：デプロイ後に別途 Lambda 関数を実行する必要がありません
3. **迅速な検証**：デプロイ後すぐにナレッジベースが利用可能になります

この機能は `post_deploy.tf` ファイルで実装されており、`null_resource` と `local-exec` プロビジョナーを使用して、すべてのモジュール（OpenSearch、Bedrock、Lambda）のデプロイ完了後に Lambda 関数を実行します。また、Lambda 関数の実行結果を確認し、エラーが発生した場合はデプロイを失敗させる機能も含まれています。

```hcl
resource "null_resource" "invoke_lambda_post_deploy" {
  depends_on = [
    module.main_stack,
    module.opensearch_index,
    module.bedrock_stack,
    module.lambda_stack
  ]

  provisioner "local-exec" {
    command = <<-EOT
      set -e
      echo "Invoking Lambda function ${module.lambda_stack.lambda_function_arn}..."
      aws lambda invoke \
        --function-name ${module.lambda_stack.lambda_function_arn} \
        --region ${var.aws_region} \
        --payload '{}' \
        --query 'StatusCode' \
        /tmp/lambda_output.json
      
      # Check if the Lambda invocation was successful (StatusCode 200)
      STATUS_CODE=$(cat /tmp/lambda_output.json)
      if [ "$STATUS_CODE" -ne 200 ]; then
        echo "Lambda invocation failed with status code $STATUS_CODE"
        exit 1
      else
        echo "Lambda invocation successful with status code $STATUS_CODE"
      fi
    EOT
  }
}
```

## 削除前の S3 バケット空処理

このプロジェクトには、`terraform destroy` コマンドを実行する前に S3 バケットを空にする機能が含まれています。この機能により、以下のメリットがあります：

1. **クリーンな削除**：S3 バケットが空でないと削除できないエラーを回避します
2. **手動操作の削減**：`terraform destroy` の前に別途 S3 バケットを空にする必要がありません
3. **一貫した削除プロセス**：すべてのリソースが確実に削除されます

この機能は `pre_destroy.tf` ファイルで実装されており、`null_resource` と `local-exec` プロビジョナーを使用して、`terraform destroy` 実行時に S3 バケットを空にします。

```hcl
resource "null_resource" "empty_s3_bucket_before_destroy" {
  depends_on = [
    module.main_stack
  ]

  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
      set -e
      echo "Emptying S3 bucket ${module.main_stack.knowledge_base_bucket_name} before deletion..."
      aws s3 rm s3://${module.main_stack.knowledge_base_bucket_name} --recursive --region ${var.aws_region}
      
      # Verify that the bucket is empty
      OBJECTS_COUNT=$(aws s3api list-objects-v2 --bucket ${module.main_stack.knowledge_base_bucket_name} --query 'length(Contents)' --output text --region ${var.aws_region} || echo "0")
      
      if [ "$OBJECTS_COUNT" != "0" ] && [ "$OBJECTS_COUNT" != "None" ]; then
        echo "Error: Failed to empty S3 bucket ${module.main_stack.knowledge_base_bucket_name}. $OBJECTS_COUNT objects remaining."
        exit 1
      else
        echo "Successfully emptied S3 bucket ${module.main_stack.knowledge_base_bucket_name}"
      fi
    EOT
  }

  triggers = {
    bucket_name = module.main_stack.knowledge_base_bucket_name
  }
}
```

## 使用方法

1. Slack チャンネルで AWS Chatbot を招待します
2. チャンネル内で質問を投げかけると、Bedrock Agent が回答を生成します
3. ナレッジベースの更新は、設定した EventBridge スケジュールに従って自動的に行われます

## Slackからナレッジベースへの接続

```
@Amazon Q
connector add agent {Bedrock Agent ARN} {Bedrock AgentのエイリアスID}
```

## トラブルシューティング

- Slack 連携に問題がある場合は、AWS Chatbot の設定を確認してください
- Bedrock Agent の応答に問題がある場合は、CloudWatch Logs でエラーを確認してください
- ナレッジベースの更新に問題がある場合は、Lambda 関数のログを確認してください

## セキュリティ考慮事項

- GitHub PAT は AWS Systems Manager Parameter Store に安全に保存されます
- OpenSearch クラスターは暗号化されています
- IAM ロールは最小権限の原則に従って設定されています