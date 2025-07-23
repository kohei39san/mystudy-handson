# Windows マネージドインスタンスのセットアップ

このTerraform構成は、AWS Systems Managerで管理されるWindows Server 2022のEC2インスタンスを作成します。以下のリソースが含まれています：

## リソース構成

### ネットワークリソース
- VPC
- パブリックサブネット
- インターネットゲートウェイ
- インターネットゲートウェイへのルートを持つルートテーブル
- Windowsインスタンス用のセキュリティグループ

### コンピューティングリソース
- Windows ServerのEC2インスタンス：
  - Windows Server 2022 AMI（AWSから最新バージョン）
  - Systems Manager管理用のIAMインスタンスプロファイル
  - 必要に応じて直接アクセスするためのキーペア

### IAMリソース
- EC2信頼関係を持つIAMロール
- AmazonSSMManagedInstanceCoreのIAMポリシーアタッチメント
- EC2インスタンス用のIAMインスタンスプロファイル

## 使用方法

この構成をデプロイするには、メインのREADME.mdファイルの手順に従ってください。

デプロイ後、直接RDPアクセスを必要とせずにAWS Systems Managerを通じてこのWindowsインスタンスを管理できます。ただし、必要に応じてキーペアを使用したRDPも利用可能です。