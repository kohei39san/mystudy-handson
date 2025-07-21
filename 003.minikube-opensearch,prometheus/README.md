# MinikubeとOpenSearchのセットアップ

このTerraform構成は、MinikubeとOpenSearchがインストールされたEC2インスタンスを作成します。以下のリソースが含まれています：

## リソース構成

### ネットワークリソース
- 変数で定義されたCIDRブロックを持つVPC（デフォルト：10.0.0.0/16）
- パブリックサブネット（変数で定義されたCIDRブロック）
- インターネットゲートウェイ
- インターネットゲートウェイへのルートを持つルートテーブル
- インスタンス用のセキュリティグループ（クライアントのIPアドレスからのみSSHアクセス可能）

### コンピューティングリソース
- EC2インスタンス：
  - DockerとMinikubeのインストールスクリプト
  - 環境設定用のブートストラップ構成
  - SSHアクセス用のキーペア

### Kubernetesリソース
- OpenSearchデプロイ構成：
  - OpenSearchマスターノード（Prometheusエクスポータープラグイン付き）
  - OpenSearchデータノード（Prometheusエクスポータープラグイン付き）
  - スナップショットリポジトリ登録
  - SLM（Snapshot Lifecycle Management）構成

### IAMリソース
- EC2インスタンス用のIAMロールとポリシー

## 使用方法

このコンフィギュレーションをデプロイするには、メインのREADME.mdファイルの指示に従ってください。

デプロイ後、以下にアクセスできます：
- OpenSearchダッシュボード
- OpenSearchのPrometheusメトリクスエンドポイント（/_prometheus/metrics）

追加情報については、`docs`ディレクトリのドキュメントを参照してください。