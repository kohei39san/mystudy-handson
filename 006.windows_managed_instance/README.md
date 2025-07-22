# Windows マネージドインスタンスのセットアップ

このTerraform構成は、AWS Systems Managerで管理されるWindows Server 2022 EC2インスタンスを作成します。以下のリソースが含まれています：

## リソース構成

### ネットワークリソース
- VPC
- パブリックサブネット
- インターネットゲートウェイ
- インターネットゲートウェイへのルートを持つルートテーブル
- Windowsインスタンス用のセキュリティグループ（クライアントIPからのRDPアクセスを許可）

### コンピューティングリソース
- Windows ServerのEC2インスタンス：
  - Windows Server 2022 AMI（AWSから最新バージョン）
  - Systems Manager管理用のIAMインスタンスプロファイル
  - 必要に応じた直接アクセス用のキーペア

### IAMリソース
- EC2信頼関係を持つIAMロール
- AmazonSSMManagedInstanceCoreポリシーのアタッチメント
- EC2インスタンス用のIAMインスタンスプロファイル

## 使用方法

このコンフィギュレーションをデプロイするには、メインのREADME.mdファイルの指示に従ってください。

デプロイ後、このWindowsインスタンスは直接のRDPアクセスを必要とせずにAWS Systems Managerを通じて管理できますが、必要に応じてキーペアを使用したRDPアクセスも可能です。