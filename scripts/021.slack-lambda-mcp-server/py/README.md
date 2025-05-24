# Slack Lambda MCP Server - ローカルテスト

## 概要

このディレクトリには、Slack Lambda MCP Server をローカル環境でテストするためのスクリプトが含まれています。

## 設定方法

### AWS Systems Manager パラメータストアの設定

ローカルテストでは、以下のパラメータを AWS Systems Manager パラメータストアに設定する必要があります：

#### テスト用メッセージデータ
- `/slack-mcp-server/test/userId` - テスト用のSlackユーザーID
- `/slack-mcp-server/test/channelId` - テスト用のSlackチャンネルID
- `/slack-mcp-server/test/responseTs` - テスト用のSlackメッセージタイムスタンプ
- `/slack-mcp-server/test/text` - テスト用のメッセージテキスト

#### 環境変数
- `/slack-mcp-server/openrouter/api-key-param` - OpenRouter API キーを格納するパラメータ名
- `/slack-mcp-server/openrouter/model` - 使用するOpenRouterモデル名
- `/slack-mcp-server/dynamodb/table` - 会話履歴を保存するDynamoDBテーブル名

### パラメータの設定例

AWS CLIを使用して、以下のようにパラメータを設定できます：

```bash
# テスト用メッセージデータ
aws ssm put-parameter --name "/slack-mcp-server/test/userId" --value "U12345678" --type String --overwrite
aws ssm put-parameter --name "/slack-mcp-server/test/channelId" --value "C12345678" --type String --overwrite
aws ssm put-parameter --name "/slack-mcp-server/test/responseTs" --value "1234567890.123456" --type String --overwrite
aws ssm put-parameter --name "/slack-mcp-server/test/text" --value "AWS Lambda について教えてください" --type String --overwrite

# 環境変数
aws ssm put-parameter --name "/slack-mcp-server/openrouter/api-key-param" --value "/openrouter/api-key" --type String --overwrite
aws ssm put-parameter --name "/slack-mcp-server/openrouter/model" --value "anthropic/claude-3-opus:beta" --type String --overwrite
aws ssm put-parameter --name "/slack-mcp-server/dynamodb/table" --value "slack-mcp-bot-conversations" --type String --overwrite
```

## スクリプトの実行方法

### ローカルテスト

```bash
python local_test.py
```

このスクリプトを実行すると、以下の2つのテストオプションが表示されます：
1. Lambda ハンドラー関数をテスト
2. Slack メッセージ処理関数を直接テスト

### SSM 統合テスト

```bash
python test_ssm_integration.py
```

このスクリプトは、SSM パラメータストアとの統合をテストします。テスト用のパラメータを作成し、正しく読み込めることを確認します。

## 注意事項

- ローカルテストを実行するには、AWS 認証情報が正しく設定されている必要があります。
- テスト実行前に、必要なパラメータが SSM パラメータストアに設定されていることを確認してください。
- デフォルト値は設定されていますが、実際のテストでは適切な値を SSM パラメータストアに設定することをお勧めします。