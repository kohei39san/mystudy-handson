# EC2 Instance Connect Endpoint (EICE) 構成

このTerraform構成は、EC2 Instance Connect Endpoint (EICE) を使用してプライベートサブネット内のEC2インスタンスに安全にアクセスできる環境を構築します。

## リソース構成

### ネットワークリソース
- CIDRブロック10.0.0.0/16のVPC
- プライベートサブネット（10.0.1.0/24）
- パブリックサブネット（10.0.0.0/24）
- インターネットゲートウェイ
- NATゲートウェイ（プライベートサブネットのアウトバウンド通信用）
- ルートテーブル（パブリック・プライベート用）
- セキュリティグループ（EICE用、EC2用）

### コンピューティングリソース
- EC2インスタンス：
  - 最新のAmazon Linux 2 AMI
  - プライベートサブネット内に配置
  - SSM管理用のIAMインスタンスプロファイル
  - カスタマイズ可能なルートボリュームサイズ

### EC2 Instance Connect Endpoint (EICE)
- プライベートサブネット内のEC2インスタンスへの安全なアクセスを提供
- パブリックIPアドレスを必要とせずにSSH接続が可能
- AWS CLIまたはAWSコンソールからの接続をサポート

### 自動化スクリプト
以下のインストールスクリプトが含まれています：
- `install-ansible.sh`: Ansibleのインストール
- `install-ansible-in-wslubuntu24.04.sh`: WSL Ubuntu 24.04でのAnsibleインストール
- `install-gh.sh`: GitHub CLIのインストール

### 設定ファイル
- `aws.conf`: AWS CLI設定
- `sshd_config`: SSH設定

### IAM設定
- EC2インスタンス用のIAMロール
- SSM管理に必要な権限を付与
- EC2 Instance Connect使用に必要な権限

## 使用方法

この構成をデプロイするには、メインのREADME.mdに記載されている手順に従ってください。

### EICE経由での接続方法

```bash
# AWS CLIを使用した接続
aws ec2-instance-connect ssh --instance-id <instance-id> --os-user ec2-user
```

## 注意事項

- EC2 Instance Connect Endpointは比較的新しいサービスです
- プライベートサブネット内のインスタンスでもEICE経由で安全にアクセス可能です
- NATゲートウェイの料金が発生します