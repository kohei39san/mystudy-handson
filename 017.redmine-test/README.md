# Redmine EC2 インスタンス

このTerraformコードは、AWSのEC2インスタンス上にRedmineをデプロイするためのものです。

## 前提条件

- Terraform がインストールされていること
- AWS CLIがインストールされ、設定されていること
- SSHキーペアが用意されていること

## 使用方法

1. 以下のコマンドでTerraformを初期化します：

```bash
terraform init
```

2. 以下のコマンドで設定を適用します：

```bash
terraform apply -var="public_key_path=/path/to/your/public/key.pub" -var="allowed_ip=あなたのIP/32"
```

## Redmineへのアクセス

デプロイが完了すると、以下の情報が出力されます：

- Redmineのパブリック IP アドレス
- RedmineのURL
- SSHアクセスコマンド

### Redmineへのログイン

1. ブラウザで `http://<redmine_public_ip>` にアクセスします
2. デフォルトのログイン情報：
   - ユーザー名: admin
   - パスワード: admin

**注意**: 初回ログイン後、必ずパスワードを変更してください。

### SSHアクセス

インスタンスにSSHでアクセスするには：

```bash
ssh -i <秘密鍵のパス> ec2-user@<redmine_public_ip>
```

## データベース情報

Redmineは内部でMariaDBを使用しています：

- データベース名: redmine
- ユーザー名: redmine
- パスワード: redmine

## 注意事項

- このデプロイメントは、指定されたIPアドレスからのアクセスのみを許可しています
- 本番環境で使用する場合は、より強固なセキュリティ設定を行ってください
- バックアップを定期的に取得することをお勧めします