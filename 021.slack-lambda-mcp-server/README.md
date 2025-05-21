# Slack チャットボット with OpenRouter & AWS MCP Server

## 概要

このプロジェクトは、AWS Lambda を使用して OpenRouter、AWS Documentation MCP Server、Amazon Bedrock Knowledge Bases Retrieval MCP Server を統合した Slack チャットボットを実装します。

## システム構成

- **Slack アプリ**: チャンネルメンバーからのメッセージを受け取ります
- **Slack 受信 Lambda**: Slack からのメッセージを受け取り、SNS トピックにメッセージを送信します
- **MCP Server Lambda**: SNS からメッセージを受け取り、MCP Server を起動して OpenRouter に問い合わせを行い、Slack アプリへ返信します
- **DynamoDB**: Slack メッセージと Lambda のやり取りをキャッシュします
- **Amazon Bedrock ナレッジベース**: S3 をデータソースに持つナレッジベースを提供します
- **GitHub 同期 Lambda**: 定期的にプライベート GitHub リポジトリを S3 に送信します
- **EventBridge**: GitHub 同期 Lambda を定期的に実行するスケジューラーとして機能します
- **S3**: データソースを配置するストレージとして機能します
- **マネージド OpenSearch**: ベクトルデータベースとして機能します
- **SNS**: Lambda 間の非同期通信を実現します

## デプロイ方法

1. Terraform を使用してインフラストラクチャをデプロイします
```bash
cd 021.slack-lambda-mcp-server
terraform init
terraform apply
```

2. Slack アプリを作成し、マニフェストファイルを使用して設定します
3. 必要な環境変数を AWS Systems Manager パラメータストアに設定します

## 機能

- Slack チャンネルでのメッセージに対して AI アシスタントが応答
- AWS ドキュメントや独自のナレッジベースを参照した回答の生成
- 会話履歴の保持によるコンテキスト認識の応答
- ストリーミングレスポンスによるリアルタイムな応答表示

## セキュリティ

- IAM ロールによる最小権限の原則に基づいたアクセス制御
- Systems Manager パラメータストアを使用した認証情報の安全な管理
- Slack アプリは OAuth による最小限のアクセス許可のみを要求

## アーキテクチャ図

```
+-------------+     +----------------+     +-----+     +----------------+
| Slack App   | --> | Slack Receiver | --> | SNS | --> | MCP Server     |
+-------------+     | Lambda         |     +-----+     | Lambda         |
                    +----------------+                 +----------------+
                                                              |
                                                              v
+--------------+     +------------+     +----------------+    |
| GitHub Repo  | --> | GitHub     | --> | S3 Bucket      | <--+
+--------------+     | Sync       |     +----------------+
                     | Lambda     |            |
                     +------------+            v
                                       +----------------+     +------------+
                                       | Bedrock        | --> | OpenSearch |
                                       | Knowledge Base |     +------------+
                                       +----------------+
```