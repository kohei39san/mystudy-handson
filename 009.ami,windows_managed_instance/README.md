# Windows管理インスタンスAMI作成構成

このTerraform構成は、Windows ServerのEC2インスタンスを作成し、管理ツールをインストールした後、AMIとして保存する仕組みを提供します。

## リソース構成

### ネットワークリソース
- CIDRブロック10.0.0.0/16のVPC
- パブリックサブネット（10.0.0.0/24）
- インターネットゲートウェイ
- インターネットゲートウェイへのルートを持つルートテーブル
- Windowsインスタンス用のセキュリティグループ（RDPアクセス許可）

### コンピューティングリソース
- Windows Server EC2インスタンス：
  - 指定されたWindows Server AMI
  - SSM管理用のIAMインスタンスプロファイル
  - キーペアによるアクセス
  - カスタマイズ可能なルートボリュームサイズ

### AMI管理リソース
- Windows管理インスタンスからのAMI作成
- 管理ツールがプリインストールされたカスタムAMI

### 管理スクリプト
以下のPowerShellスクリプトが含まれています：
- `enable-userdata.ps1`: ユーザーデータの有効化
- `install-amazoncloudwatch-service.ps1`: Amazon CloudWatchエージェントのインストール
- `install-zabbixagent-service.ps1`: Zabbixエージェントのインストール

### IAM設定
- EC2インスタンス用のIAMロール
- SSM管理に必要な権限を付与
- CloudWatchエージェント実行に必要な権限

## 使用方法

この構成をデプロイするには、メインのREADME.mdに記載されている手順に従ってください。

## 注意事項

- Windows Serverのライセンス料金が発生します
- AMI作成には時間がかかる場合があります
- 管理ツールのインストールは自動化されていますが、設定は手動で行う必要があります