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

## 変数のオーバーライド

変数を上書きするには、以下の2つの方法があります：

1. コマンドラインで `-var` オプションを使用する方法（上記の例）
2. `override.tf` ファイルを作成して変数を上書きする方法

### override.tf の使用方法

`override.tf` ファイルを作成することで、変数をより永続的に上書きすることができます。以下は `override.tf` の記載例です：

```hcl
# override.tf の例
variable "instance_type" {
  default = "t3.micro"  # t2.micro から t3.micro に変更
}

variable "allowed_ip" {
  default = "203.0.113.0/24"  # 許可するIPアドレス範囲を指定
}

variable "private_key_path" {
  default = "~/.ssh/redmine_key"  # 秘密鍵のパスを指定
}
```

`override.tf` ファイルは `.gitignore` に追加することで、個人の設定を共有リポジトリにコミットせずに管理できます。

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

インスタンスにSSHでアクセスするには、EC2 Instance Connect を使用します：

```bash
aws ec2-instance-connect ssh --instance-id <インスタンスID> --os-user bitnami --private-key-file <秘密鍵のパス>
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