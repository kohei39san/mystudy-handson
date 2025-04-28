# Bedrock ウェブクローラー CloudFormation アーキテクチャ

## 概要

このプロジェクトは、Amazon BedrockとAWS CloudFormationを使用してウェブクローラーアーキテクチャを実装します。BedrockのClaude 3.5 Sonnet v2モデルを使用してウェブコンテンツを解析し、OpenSearchをベクトルデータベースとして使用します。クローリング対象のURLはCloudFormationのパラメータとして指定します。

## アーキテクチャ

```mermaid
graph TB
    Bedrock[Amazon Bedrock<br/>Claude 3.5 Sonnet v2] --> OpenSearch[OpenSearch<br/>ベクトルDB]
    EventBridge[EventBridge<br/>スケジューラー] --> Lambda[AWS Lambda<br/>クローラー]
    Lambda --> Bedrock
    Bedrock --> WebCrawler[Bedrock データソース<br/>ウェブクローラー]
```

## コンポーネント

1. **Amazon Bedrock**:
   - Claude 3.5 Sonnet v2モデルを使用
   - ウェブページからの情報抽出と解析
   - テキストのベクトル化と意味解析
   - クローリング対象URLの管理

2. **OpenSearch**:
   - ベクトルデータベースとして機能
   - 解析結果の効率的な検索と保存
   - コンテンツの類似性分析
   - ベクトルインデックスの最適化

3. **Lambda関数**:
   - Bedrockデータソースの設定
   - クローリング対象URLの管理
   - エラーハンドリング

4. **EventBridge**:
   - クローリングの定期実行
   - スケジュール管理

## CloudFormationテンプレート構造

```yaml
Parameters:
  CrawlingUrls:
    Type: CommaDelimitedList
    Description: クロール対象のURLリスト（カンマ区切り）

Resources:
  # IAMロール
  CrawlerLambdaRole:
    Type: AWS::IAM::Role
    # Lambda用のBedrock、OpenSearchアクセス権限

  # OpenSearchドメイン
  VectorStore:
    Type: AWS::OpenSearchService::Domain
    # ベクトルエンジン設定

  # Lambda関数
  CrawlerFunction:
    Type: AWS::Lambda::Function
    # ウェブクローラーの実装

  # EventBridge
  CrawlerSchedule:
    Type: AWS::Events::Rule
    # スケジューリング設定
```

## 前提条件

1. AWS CLIのインストールと設定
2. Amazon Bedrockサービスへのアクセス権限
3. CloudFormationデプロイ用の適切なIAM権限
4. OpenSearchサービスの利用権限

## デプロイ方法

1. このリポジトリをクローン
2. `014.bedrock-webcrawler`ディレクトリに移動
3. CloudFormationスタックのデプロイ：
   ```bash
   aws cloudformation create-stack \
     --stack-name bedrock-webcrawler \
     --template-body file://template.yaml \
     --parameters \
       ParameterKey=CrawlingUrls,ParameterValue=\"https://example.com,https://example.org\" \
     --capabilities CAPABILITY_IAM
   ```

## パラメータの説明

1. **CrawlingUrls** (必須):
   - 型: CommaDelimitedList
   - 説明: クロール対象のURLリスト（カンマ区切り）
   - 例: `"https://example.com,https://example.org"`

2. **CrawlingInterval** (オプション):
   - 型: String
   - デフォルト: `rate(1 hour)`
   - 説明: クローリングの実行間隔
   - 例: `rate(30 minutes)`, `rate(2 hours)`

3. **OpenSearchInstanceType** (オプション):
   - 型: String
   - デフォルト: `r6g.large.search`
   - 説明: OpenSearchのインスタンスタイプ

4. **BedrockMaxTokens** (オプション):
   - 型: Number
   - デフォルト: 4096
   - 説明: Bedrockモデルの最大トークン数

## セキュリティ考慮事項

1. **IAMロール**: Lambda関数に対する最小権限アクセス
2. **OpenSearchセキュリティ**: 暗号化とアクセス制御
3. **ネットワークセキュリティ**: VPCエンドポイントとセキュリティグループ

## モニタリングとログ

1. **CloudWatchログ**: 
   - Lambda関数の実行ログ
   - クローリング状態の監視
   - エラー情報の確認

2. **OpenSearchダッシュボード**:
   - ベクトルデータの可視化
   - インデックスの状態監視
   - クエリパフォーマンスの分析

## コスト考慮事項

1. **Bedrock**: 
   - Claude 3.5 Sonnet v2の使用料金
   - トークン数に応じた課金

2. **OpenSearch**: 
   - インスタンス料金
   - ストレージ料金
   - データ転送料金

3. **Lambda**: 
   - 実行時間に応じた料金
   - メモリ使用量による課金

## エラー処理

1. **クローリングエラー**:
   - 無効なURL
   - アクセス制限
   - タイムアウト

2. **Bedrockエラー**:
   - モデル呼び出しの失敗
   - トークン制限の超過
   - APIエラー

3. **システムエラー**:
   - Lambda関数のタイムアウト
   - メモリ不足
   - ネットワークエラー

エラーはCloudWatchログに記録され、必要に応じてアラートを設定できます。

## 料金概算

1か月あたりの概算費用（東京リージョン）：

### OpenSearch Service
- t3.small.search × 1台: $30.24/月
- EBS gp3 10GB: $1.00/月
小計: $31.24/月

### Lambda
- メモリ: 256MB
- 実行時間: 5分 × 4回/月 = 20分
- 料金: Free Tier内（実質無料）
小計: $0/月

### Amazon Bedrock
- Titan Embed Text V2
  - 入力: $0.0001/1Kトークン
  - 週1回のクロール × 4週 = 月4回
  - 1回あたり約10,000トークン = 月40,000トークン
小計: $0.004/月

### VPCリソース
- NAT Gateway: $32.40/月
  - 時間料金: $0.045/時 × 24時間 × 30日
  - データ処理: 約$1/月
- VPCエンドポイント: $7.20/月
  - $0.01/時 × 24時間 × 30日
小計: $40.60/月

### 合計推定費用
- USD: $71.844/月（税抜）
- JPY: ¥10,777/月（税抜）※1USD=150円で計算

※ この見積もりは以下の前提に基づきます：
- OpenSearchは24時間365日稼働
- Lambda関数は週1回、5分間実行
- データ転送量は最小限
- すべて東京リージョンでの料金
