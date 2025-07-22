# Windows マネージドインスタンスのセットアップ

このTerraform構成は、AWS Systems Managerで管理されるWindows Server 2022 EC2インスタンスを作成します。以下のリソースが含まれています：

## リソース構成

### ネットワークリソース
- VPC
- パブリックサブネット
- インターネットゲートウェイ
- インターネットゲートウェイへのルートを持つルートテーブル
- Windowsインスタンス用のセキュリティグループ

### コンピュートリソース
- Windows Server EC2インスタンス:
  - Windows Server 2022 AMI（AWSの最新バージョン）
  - Systems Manager管理用のIAMインスタンスプロファイル
  - 必要に応じて直接アクセスするためのキーペア

### IAMリソース
- EC2信頼関係を持つIAMロール
- AmazonSSMManagedInstanceCoreのIAMポリシーアタッチメント
- EC2インスタンス用のIAMインスタンスプロファイル

## 使用方法

この構成をデプロイするには、メインのREADME.mdファイルに記載されている手順に従ってください。

デプロイ後、直接のRDPアクセスを必要とせずにAWS Systems Managerを通じてこのWindowsインスタンスを管理できます。ただし、必要に応じてキーペアを使用したRDPアクセスも可能です。