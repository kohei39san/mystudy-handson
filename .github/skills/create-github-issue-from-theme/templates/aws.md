## 背景・課題

<!-- 現状のインフラ構成の問題点・要件 -->

## 目的・ゴール

<!-- 構築/変更後に達成されること / Definition of Done -->

- [ ] 

## IaC 実装方針

<!-- IaC 方針を明記する（cloudformation / terraform / auto） -->
<!-- スタック方針を明記する（single / split） -->

- **IaC モード**: 
- **スタック方針**: 
- **補足方針**: <!-- 例: CloudFormation を第一選択とし、不足分のみ別手段で補完 -->

## 作成するファイル一覧

<!-- `docs/directory-structure.md` のルールに従って記載する -->

| ファイルパス | 種別 | 用途 |
|---|---|---|
|   | 新規/更新 |   |

## 想定フォルダ構成

<!-- `docs/directory-structure.md` のルールに従って記載する -->
<!-- CloudFormation の場合は機能ディレクトリ/cfn 配下を利用すること -->

```text
<機能ディレクトリ>/
	cfn/
		infrastructure.yaml
	README.md
	src/
```

## 変数一覧（デプロイ必須のみ・機密区分）

<!-- デプロイに不要な変数は記載しない -->
<!-- 機密区分は最低でも「公開可 / 内部情報」を付与する -->

| 変数名 | 用途 | 例 | 機密区分 | 備考 |
|-------|------|----|---------|------|
|       |      |    | 公開可/内部情報 | |

### 機密値の取り扱いルール

- 機密区分が `内部情報` の値は、Issue 本文・公開コメントに実値を記載しない
- 実値の保存は平文コミットを避ける（例: SSM Parameter Store / Secrets Manager）

## 依存関係・前提条件

<!-- 先行して完了している必要がある Issue / リソース / 設定を記載する -->

| 種別 | 内容 | 状態 |
|------|------|------|
| 前提 Issue | <!-- #番号 タイトル --> | open/closed |
| 前提リソース | <!-- 既存の VPC, S3 バケット等 --> | 有/無 |
| 前提条件 | <!-- IAM ロールの存在、証明書の発行等 --> |  |

## 対象 AWS サービス

<!-- 関連する AWS サービス一覧 -->

| サービス | 用途 |
|---------|------|
|         |      |

## アーキテクチャ概要

<!-- リソース構成・アーキテクチャの概略（テキスト or 図） -->
<!-- 例: draw.io / Mermaid / テキスト構成図 -->

## ネットワーク設計

<!-- リソースに応じて必要な行のみ記載する -->
<!-- 対象外の場合は N/A または「対象外（理由）」とし、変数名は記載しない -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/whitepapers/latest/aws-vpc-connectivity-options/introduction.html -->

| パラメータ | 値 | 備考 |
|----------|----|------|
| VPC CIDR |    |      |
| パブリックサブネット CIDR |  |  |
| プライベートサブネット CIDR | |  |
| AZ 構成 |     |      |
| インターネットゲートウェイ | 有/無 | |
| NAT ゲートウェイ | 有/無 |  |
| VPC エンドポイント |  |      |

### セキュリティグループ / NACL パラメータ

<!-- 適用するリソース分だけ行を追加する -->

| SG/NACL 名 | 方向 | プロトコル | ポート | 送信元/宛先 | 用途 |
|-----------|------|-----------|--------|------------|------|
|           |      |           |        |            |      |

## IAM 設計

<!-- ロール・ポリシー・最小権限の原則に基づく設計 -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/sec_permissions_least_privileges.html -->

| ロール/ポリシー名 | 対象サービス | 付与する権限 | 備考 |
|----------------|-------------|------------|------|
|                |             |            |      |

## リソース仕様

<!-- インスタンスタイプ・ストレージ・スペック等の詳細 -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/welcome.html -->
<!-- BP(備考欄に記載): https://aws.amazon.com/ec2/instance-types/ -->

| リソース | 仕様 | 台数/容量 | 備考 |
|---------|------|----------|------|
|         |      |          |      |

## タグ設計

<!-- リソース管理・コスト配分・SCP 適用に使用するタグを定義する -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/tag-editor/latest/userguide/tagging.html -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/tagging-best-practices.html -->

| タグキー | 値の例 | 必須 | 備考 |
|---------|--------|------|----- |
| `Name` |        | ✅   |      |
| `Env` | `dev` / `staging` / `prod` | ✅ | |
| `Owner` | <!-- チーム名・担当者 --> | ✅ | SCP でタグ必須を強制 |
| `Project` |      | ✅   |      |
| `CostCenter` |   | ❌   | コスト配分用 |

## セキュリティ設計

<!-- 暗号化・シークレット管理・コンプライアンス対応 -->
<!-- BP(各項目直下に記載): https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html -->
<!-- BP(各項目直下に記載): https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html -->
<!-- BP(各項目直下に記載): https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html -->

- **保存データの暗号化**: <!-- KMS キー設計、対象リソース -->
- **転送データの暗号化**: <!-- TLS バージョン、証明書管理 -->
- **シークレット管理**: <!-- Secrets Manager / SSM Parameter Store の使い分け -->
- **ログ・監査**: <!-- CloudTrail, Config, VPC Flow Logs の有効化方針 -->

## 可用性・冗長化設計

<!-- マルチ AZ 構成・フェイルオーバー・スケーリング方針 -->
<!-- 対象外の場合は N/A または「対象外（理由）」とし、変数名は記載しない -->
<!-- BP(各項目直下に記載): https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html -->
<!-- BP(各項目直下に記載): https://docs.aws.amazon.com/whitepapers/latest/real-time-communication-on-aws/high-availability-and-scalability-on-aws.html -->

- **マルチ AZ**: <!-- 対応サービスと AZ 数 -->
- **Auto Scaling**: <!-- スケールイン/アウトの条件 -->
- **ヘルスチェック**: <!-- ELB ターゲットグループ, Route 53 フェイルオーバー等 -->
- **目標 RTO / RPO**: RTO: 　 / RPO: 

## バックアップ・DR 設計

<!-- スナップショット・クロスリージョンレプリケーション・リストア手順 -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/back-up-data.html -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/aws-backup/latest/devguide/best-practices.html -->

| 対象リソース | バックアップ方式 | 保持期間 | リストア手順 |
|------------|----------------|---------|------------|
|            |                |         |            |

## 監視・アラート設計

<!-- CloudWatch メトリクス・アラーム・ダッシュボード・通知先 -->
<!-- 対象外の場合は N/A または「対象外（理由）」とし、変数名は記載しない -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/welcome.html -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/best-practices-metric-math.html -->

| メトリクス | 閾値 | アクション | 通知先 |
|-----------|------|----------|--------|
|           |      |          |        |

## コスト見積もり

<!-- 月額概算コスト（AWS Pricing Calculator 等を参照） -->
<!-- BP(備考欄に記載): https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html -->
<!-- BP(備考欄に記載): https://calculator.aws/pricing/2/home -->

| リソース | 概算月額 | 備考 |
|---------|---------|------|
|         |         |      |
| **合計** |         |      |

## 実施内容

<!-- Terraform / CloudFormation / CDK の実装タスク -->

- [ ] 
- [ ] 

## デプロイ・移行手順

<!-- 本番適用時の手順・ロールバック方針 -->

1. 
2. 

**ロールバック手順:**

1. 

## テスト・検証方針

### 静的解析・Lint

<!-- コードの構文・ポリシー違反の事前チェック -->
<!-- IaC 方針に応じて不要な行は N/A にする（Terraform 主体なら CFn 行は任意、CFn 主体なら Terraform 行は任意） -->
<!-- 非採用 IaC の行は削除せず、対象列に `N/A（本Issueでは非採用）` を明記する -->
<!-- BP(ツール列の備考に記載): https://developer.hashicorp.com/terraform/language/style -->
<!-- BP(ツール列の備考に記載): https://github.com/terraform-linters/tflint -->
<!-- BP(ツール列の備考に記載): https://www.checkov.io/1.Welcome/Quick%20Start.html -->

| ツール | 対象 | 実行タイミング |
|-------|------|-------------|
| `terraform validate` / `terraform fmt` | Terraform 構文 | PR 時 |
| `tflint` | Terraform ベストプラクティス | PR 時 |
| `checkov` / `tfsec` | セキュリティポリシー違反 | PR 時 |
| `cfn-lint` | CloudFormation テンプレート | PR 時（CFn 利用時） |

### IaC別チェック方針

- **CloudFormation 主体**:
	- `cfn-lint` と Change Set 検証を必須にする
	- 必要に応じて `checkov` でテンプレートのセキュリティチェックを行う
- **Terraform 主体**:
	- `terraform fmt` / `terraform validate` / `tflint` を必須にする
	- 必要に応じて `checkov` / `tfsec` を実施する

**CI 実装（GitHub Actions）:**

- [ ] `.github/workflows/` に lint ワークフローを作成する
- [ ] 使用するツールをワークフローにインストール・実行するステップを追加する
- [ ] PR トリガー（`on: pull_request`）で自動実行されるよう設定する
- [ ] lint エラー時に PR をブロックするブランチ保護ルールを設定する

### ユニットテスト・モックテスト

<!-- AWS API をモック化して実リソースを作成せずに検証する -->
<!-- BP(ツール列の備考に記載): https://docs.localstack.cloud/getting-started/ -->
<!-- BP(ツール列の備考に記載): https://docs.getmoto.org/en/latest/docs/getting_started.html -->
<!-- BP(ツール列の備考に記載): https://terratest.gruntwork.io/docs/getting-started/quick-start/ -->

| ツール | 用途 | モック対象 |
|-------|------|---------|
| `localstack` | AWS サービス全般のローカルエミュレーション | S3, SQS, Lambda, DynamoDB 等 |
| `moto` (Python) | boto3 呼び出しのモック | AWS API レスポンス |
| `aws-cdk` assertions | CDK スタックのスナップショットテスト | CloudFormation テンプレート出力 |
| `terratest` (Go) | Terraform モジュールの結合テスト | 実環境または LocalStack |

```
# 例: moto を使ったモックテスト対象
- [ ] S3 バケット作成・ポリシー設定
- [ ] Lambda 関数の呼び出しと戻り値
- [ ] IAM ポリシーの評価結果（aws iam simulate-principal-policy）
```

**CI 実装（GitHub Actions）:**

- [ ] `.github/workflows/` にテストワークフローを作成する
- [ ] `LocalStack` をサービスコンテナ（`services:`）または `setup-localstack` アクションで起動する
- [ ] テスト実行ステップ（`pytest` 等）を追加し、結果を `junit` 形式で出力する
- [ ] `actions/upload-artifact` でテスト結果レポートを保存する
- [ ] PR トリガーでテスト失敗時にマージをブロックするよう設定する

### 結合テスト（実環境）

<!-- dev/staging 環境へのデプロイ後に行う動作確認 -->
<!-- IaC 方針に応じて、CloudFormation か Terraform の手順を選択する -->
<!-- 非採用 IaC の手順は削除せず、`N/A（本Issueでは非採用）` として残す -->

- [ ] `terraform plan` で差分が意図どおりか確認
- [ ] `terraform apply` を dev 環境へ適用
- [ ] `aws cloudformation create-change-set` / `describe-change-set` で差分を確認
- [ ] `aws cloudformation deploy` で dev 環境へ適用
- [ ] AWS コンソール / CLI で各リソースの設定値をパラメータシートと照合
- [ ] エンドポイント疎通確認（curl / telnet / nmap 等）
- [ ] CloudWatch Logs・メトリクスが正常に収集されることを確認

### 受け入れ基準

<!-- Issue クローズの条件 -->

- [ ] 
- [ ] 

## 参考情報

### 関連 Issue

<!-- 類似 Issue が見つかった場合に記載 -->
<!-- - #<番号> <タイトル> (<状態>) - <URL> -->

### AWS 公式ドキュメント

<!-- 関連する AWS ドキュメントリンク -->

- 
