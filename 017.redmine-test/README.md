# Redmine EC2 インスタンス

このTerraformコードは、AWSのEC2インスタンス上にBitnamiのRedmineをデプロイするためのものです。

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
terraform apply -var="public_key_path=/path/to/your/public/key.pub" -var="private_key_path=/path/to/your/private/key" -var="allowed_ip=あなたのIP/32"
```

## Redmineへのアクセス

デプロイが完了すると、以下の情報が出力されます：

- Redmineのパブリック IP アドレス
- RedmineのURL
- EC2インスタンスコネクトを使用したSSHアクセスコマンド

### Redmineへのログイン

1. ブラウザで `http://<redmine_public_ip>` にアクセスします
2. デフォルトのログイン情報（Bitnami AMIの場合）：
   - ユーザー名: user
   - パスワード: インスタンスのシステムログで確認できます

**注意**: 初回ログイン後、必ずパスワードを変更してください。

### SSHアクセス

インスタンスにSSHでアクセスするには、EC2インスタンスコネクトを使用します：

```bash
aws ec2-instance-connect ssh --instance-id <インスタンスID> --os-user bitnami --private-key-file <秘密鍵のパス> --region <リージョン>
```

## データベース情報

Redmineは内部でMariaDBを使用しています：

- データベース名: bitnami_redmine
- ユーザー名: bn_redmine
- パスワード: インスタンス内の設定ファイルで確認できます

## セキュリティ情報

- このデプロイメントでは、EC2インスタンスコネクトを使用してSSH接続を行います
- セキュリティグループでは、SSH（22番ポート）へのアクセスは許可されていません
- HTTP（80番ポート）とHTTPS（443番ポート）のみ、指定されたIPアドレスからのアクセスが許可されています

## 注意事項

- このデプロイメントは、指定されたIPアドレスからのアクセスのみを許可しています
- 本番環境で使用する場合は、より強固なセキュリティ設定を行ってください
- バックアップを定期的に取得することをお勧めします