# BLEA Governance Base Control Tower

## パラメータストアの設定

AWS CLIを使用してパラメータストアを設定するには、以下のコマンドを実行します。

### 開発環境（dev）のパラメータ設定

```bash
# 環境名の設定
aws ssm put-parameter \
  --name "/blea/dev/envName" \
  --value "Development" \
  --type "SecureString" \
  --key-id "alias/aws/ssm" \
  --overwrite

# セキュリティ通知メールの設定
aws ssm put-parameter \
  --name "/blea/dev/securityNotifyEmail" \
  --value "notify-security@example.com" \
  --type "SecureString" \
  --key-id "alias/aws/ssm" \
  --overwrite

# Slack Workspace IDの設定
aws ssm put-parameter \
  --name "/blea/dev/securitySlackWorkspaceId" \
  --value "TXXXXXXXXXX" \
  --type "SecureString" \
  --key-id "alias/aws/ssm" \
  --overwrite

# Slack Channel IDの設定
aws ssm put-parameter \
  --name "/blea/dev/securitySlackChannelId" \
  --value "CXXXXXXXXXX" \
  --type "SecureString" \
  --key-id "alias/aws/ssm" \
  --overwrite
```


## デプロイ手順

### パッケージのインストール

```
npm i --package-lock-only
npm ci
npm install -D tsx
```

### デプロイ

```
npx aws-cdk bootstrap --profile default
npx aws-cdk deploy --all --profile default
```