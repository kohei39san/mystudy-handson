# Windows Managed Instance セットアップ

このTerraform構成は、AWS Systems Managerで管理されるWindows Server 2022 EC2インスタンスを作成します。

![Architecture Diagram](src/architecture.svg)

## リソース構成

### ネットワークリソース
- VPC
- パブリックサブネット
- インターネットゲートウェイ
- インターネットゲートウェイへのルートを持つルートテーブル
- Windowsインスタンス用セキュリティグループ

### コンピュートリソース
- Windows Server EC2インスタンス:
  - Windows Server 2022 AMI（AWSの最新版）
  - Systems Manager管理用IAMインスタンスプロファイル
  - 必要に応じた直接アクセス用キーペア

### IAMリソース
- EC2信頼関係を持つIAMロール
- AmazonSSMManagedInstanceCoreのIAMポリシーアタッチメント
- EC2インスタンス用IAMインスタンスプロファイル

## 使用方法

この構成をデプロイするには、メインのREADME.mdに記載されている手順に従ってください。

デプロイ後、直接RDPアクセスを必要とせずに、AWS Systems Managerを通じてこのWindowsインスタンスを管理できます。ただし、必要に応じてキーペアを使用したRDPアクセスも利用可能です。