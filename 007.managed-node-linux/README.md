# Linux Managed Node セットアップ

このTerraform構成は、AWS Systems Managerで管理され、監視機能を持つLinux EC2インスタンスを作成します。

![Architecture Diagram](src/architecture.svg)

## リソース構成

### ネットワークリソース
- VPC
- パブリックサブネット
- インターネットゲートウェイ
- インターネットゲートウェイへのルートを持つルートテーブル
- Linuxインスタンス用セキュリティグループ

### コンピュートリソース
- Linux EC2インスタンス:
  - Amazon Linux AMI（変数で指定）
  - Systems Manager管理用IAMインスタンスプロファイル
  - 必要に応じたSSHアクセス用キーペア

### IAMリソース
- EC2信頼関係を持つIAMロール
- AmazonSSMManagedInstanceCoreのIAMポリシーアタッチメント
- EC2インスタンス用IAMインスタンスプロファイル

### 監視リソース
- インストールスクリプト:
  - Amazon CloudWatch Agent
  - Zabbix Agent 6.0

## 使用方法

この構成をデプロイするには、メインのREADME.mdに記載されている手順に従ってください。

デプロイ後、以下のことが可能です:
1. AWS Systems Managerを通じてこのLinuxインスタンスを管理
2. Amazon CloudWatchを使用してインスタンスを監視
3. Zabbixを使用してインスタンスを監視（Zabbixサーバーの設定が必要）
4. 必要に応じてキーペアを使用したSSHアクセス