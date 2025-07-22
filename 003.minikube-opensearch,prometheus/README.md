# MinikubeとOpenSearch、Prometheusのセットアップ

このTerraform構成は、Minikube、OpenSearch、およびPrometheusがインストールされたEC2インスタンスを作成します。以下のリソースが含まれています：

## リソース構成

### ネットワークリソース
- VPC（CIDR: 10.0.0.0/16）
- パブリックサブネット
- インターネットゲートウェイ
- インターネットゲートウェイへのルートを持つルートテーブル
- インスタンス用のセキュリティグループ

### コンピュートリソース
- 以下を含むEC2インスタンス:
  - DockerとMinikubeのインストールスクリプト
  - 環境設定用のブートストラップ構成

### Kubernetesリソース
- OpenSearchデプロイ構成:
  - OpenSearchリーダーノード
  - OpenSearchデータノード
  - スナップショットリポジトリの登録
  - SLM（Snapshot Lifecycle Management）構成

### IAMリソース
- EC2インスタンス用のIAMロールとポリシー

## 使用方法

この構成をデプロイするには、メインのREADME.mdファイルに記載されている手順に従ってください。

デプロイ後、以下にアクセスできます：
- OpenSearchダッシュボード
- Prometheusモニタリングインターフェース

追加情報については、`docs`ディレクトリのドキュメントを参照してください。