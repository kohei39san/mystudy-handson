# BLEA Governance Base - StackSets Manager

このプロジェクトは、[024.test-custom-blea-gov-base-ct](../024.test-custom-blea-gov-base-ct) で生成された BLEA Governance Base の CloudFormation テンプレートを、AWS CloudFormation StackSets を使用して**マルチアカウント・マルチリージョン**にデプロイするための管理スタックです。

## 概要

- **目的**: AWS Control Tower 環境でのマルチアカウント・マルチリージョンへの BLEA Governance Base 展開
- **通知重複の回避**: 3つの通知モード（Centralized / Regional / None）で重複通知を制御
- **一元管理**: 管理アカウントから全ゲストアカウントへのデプロイを統一管理
- **テンプレート自動生成**: CDK Stage の synth() を使用してテンプレートを動的に生成（ファイル不要）

## ディレクトリ構成

```
039.blea-gov-base-ct-stacksets/
├── bin/
│   └── blea-gov-base-ct-stacksets.ts    # エントリーポイント
├── lib/
│   ├── construct/
│   │   └── stackset-manager.ts          # StackSet 管理 Construct
│   ├── stack/
│   │   └── blea-gov-base-ct-stackset-manager-stack.ts  # StackSet マネージャースタック
│   └── stage/
│       └── blea-gov-base-ct-template-stage.ts  # テンプレート生成用 Stage
├── parameter.ts                          # StackSet デプロイパラメータ
├── package.json
├── cdk.json
├── tsconfig.json
└── README.md
```

## 前提条件

### AWS アカウント設定

- **管理アカウント**: このスタックをデプロイするアカウント（Control Tower Organizations Management Account）
- **ゲストアカウント**: StackSet でデプロイする対象アカウント（複数可）
- **IAM 権限**: StackSet の作成・管理権限

### 依存関係

このプロジェクトは [024.test-custom-blea-gov-base-ct](../024.test-custom-blea-gov-base-ct) の Stack 定義を参照します。024ディレクトリのパッケージがインストールされている必要はありませんが、ファイルが存在している必要があります。

## セットアップ

### 1. パッケージのインストール

```bash
cd 039.blea-gov-base-ct-stacksets
npm i --package-lock-only
npm ci
```

### 2. 環境変数の設定（セキュリティ推奨）

センシティブな情報（アカウントID、リージョンなど）を parameter.ts に直接書かずに、環境変数で管理できます。

#### 2-1. .env ファイルを作成

```bash
# .env.example をコピー
cp .env.example .env

# .env を編集して実際の値を設定
```

#### 2-2. .env ファイルの編集

```bash
# StackSet 管理アカウント設定
STACK_SET_ACCOUNT=123456789012              # 管理アカウントID（必須）
STACK_SET_REGION=ap-northeast-1             # 管理アカウントのリージョン
STACK_SET_ENV_NAME=Production               # 環境名

# 通知設定
STACK_SET_NOTIFICATION_MODE=centralized     # centralized | regional | none
STACK_SET_NOTIFY_EMAIL=security-ops@example.com
STACK_SET_SLACK_WORKSPACE_ID=TXXXXXXXXXX    # オプション
STACK_SET_SLACK_CHANNEL_ID=CXXXXXXXXXX      # オプション

# S3 ライフサイクル
STACK_SET_S3_EXPIRATION_DAYS=366
STACK_SET_S3_EXPIRED_DELETE_DAYS=30

# デプロイ対象（必須）
STACK_SET_TARGET_ACCOUNTS=210987654321,321098765432    # カンマ区切り
STACK_SET_TARGET_REGIONS=ap-northeast-1,us-east-1,eu-west-1

# Organization ID
STACK_SET_ORG_ID=o-xxxxxxxxxx
```

> **重要**: `.env` ファイルは `.gitignore` に含まれており、Git にコミットされません。

#### 2-3. 環境変数の読み込み確認

parameter.ts は自動的に環境変数から値を読み込みます：

```typescript
// parameter.ts の内部実装
export const stackSetParameter: StackSetParameter = {
  env: { 
    account: getEnvOrThrow('STACK_SET_ACCOUNT'),  // 環境変数から取得
    region: getEnvOrDefault('STACK_SET_REGION', 'ap-northeast-1'),
  },
  targetAccounts: getEnvArray('STACK_SET_TARGET_ACCOUNTS'),
  targetRegions: getEnvArray('STACK_SET_TARGET_REGIONS'),
  // ...
};
```

### 3. パラメータ設定（代替方法）

環境変数を使わない場合は、[parameter.ts](parameter.ts) を直接編集することもできます。ただし、**アカウントIDなどのセンシティブな情報を含めないように注意**してください。

## 通知モード

StackSets で複数のリージョン・アカウントにデプロイする際、セキュリティアラームの通知が重複する問題を避けるため、3つの通知モードをサポートしています。

### 1. Centralized（推奨）

管理アカウントのみがセキュリティアラームを受け取ります。すべてのゲストアカウントとリージョンからのアラームが、管理アカウントの単一のメールアドレスと Slack チャネルに集約されます。

```typescript
// parameter.ts
export const stackSetParameter: StackSetParameter = {
  notificationMode: 'centralized',
  securityNotifyEmail: 'security-ops@example.com',
  securitySlackWorkspaceId: 'TXXXXXXXXXX',
  securitySlackChannelId: 'CXXXXXXXXXX',
  // ...
};
```

**メリット**:
- 通知を一元管理
- 重複通知なし
- 管理コストが低い

**デメリット**:
- リージョン/アカウント情報の可視性が必要（SNS メッセージに含める）

**通知フロー**:
```
ゲストアカウント (ap-northeast-1)
  └─ CloudWatch Alarms → SNS Topic → 管理アカウントのメール

ゲストアカウント (us-east-1)
  └─ CloudWatch Alarms → SNS Topic → 管理アカウントのメール
```

### 2. Regional

各リージョン・アカウント毎に異なるメールアドレスや Slack チャネルを指定します。

```typescript
// parameter.ts
export const stackSetParameter: StackSetParameter = {
  notificationMode: 'regional',
  regionalNotifications: {
    'ap-northeast-1': {
      email: 'security-ap@example.com',
      slackChannelId: 'CAPXXXXXXXXX',
    },
    'us-east-1': {
      email: 'security-us@example.com',
      slackChannelId: 'CUSXXXXXXXXX',
    },
    'eu-west-1': {
      email: 'security-eu@example.com',
      slackChannelId: 'CEUXXXXXXXXX',
    },
  },
  // ...
};
```

**メリット**:
- リージョン毎に異なる受信者を指定可能
- ローカルセキュリティチームへの通知

**デメリット**:
- 設定が複雑
- リージョン毎に別々のチャネルやメール管理が必要

**通知フロー**:
```
ゲストアカウント (ap-northeast-1)
  └─ SNS Subscription → ap-security@example.com

ゲストアカウント (us-east-1)
  └─ SNS Subscription → us-security@example.com
```

### 3. None

セキュリティ通知を完全に無効化します（CloudWatch Alarms は引き続き作成されるが、SNS 通知なし）。

```typescript
// parameter.ts
export const stackSetParameter: StackSetParameter = {
  notificationMode: 'none',
  // ...
};
```

**メリット**:
- 通知がない（CloudWatch Alarms は引き続き作成される）

**デメリット**:
- セキュリティイベントの通知がない
- 手動監視が必要

## デプロイ手順

### ステップ 1: StackSet マネージャーをデプロイ

**管理アカウント**で実行：

```bash
# CDK Bootstrap（初回のみ）
npx cdk bootstrap

# StackSet マネージャースタックをデプロイ
npx cdk deploy Dev-BLEAGovBaseCtStackSetManager
```

テンプレートは自動的に生成されるため、事前の `cdk synth` は不要です。

### ステップ 2: デプロイ確認

AWS Management Console → CloudFormation → StackSets で以下を確認：

1. **StackSet 作成**: `BLEA-Governance-Base-ControlTower` が作成されている
2. **Stack Instances**: 各ゲストアカウント × 各リージョンのスタックが作成中
3. **通知受信**: 設定したメールアドレスに確認メール

```bash
# CLI で確認
aws cloudformation list-stack-instances \
  --stack-set-name BLEA-Governance-Base-ControlTower
```

## 運用

### StackSet の更新

パラメータやテンプレートを更新する場合：

1. 024ディレクトリで変更を加えて `npm run synth`
2. 039ディレクトリの `parameter.ts` を更新（必要に応じて）
3. `npx cdk deploy` を再実行

StackSets は自動的に全インスタンスに変更を適用します。

### 新しいアカウント/リージョンの追加

`parameter.ts` の `targetAccounts` または `targetRegions` に追加して再デプロイ：

```typescript
targetAccounts: ['210987654321', '321098765432', '432109876543'],  // ← 追加
targetRegions: ['ap-northeast-1', 'us-east-1', 'eu-west-1', 'ap-southeast-1'],  // ← 追加
```

### トラブルシューティング

#### スタックインスタンスがエラー

AWS Console で StackSet → Stack Instances を確認し、エラーメッセージを確認してください。

```bash
aws cloudformation list-stack-instances \
  --stack-set-name BLEA-Governance-Base-ControlTower \
  --query 'Summaries[?Status==`FAILED`]'
```

#### 通知が重複して受け取っている

- `notificationMode` が `'regional'` になっていないか確認
- 複数のスタックが同じメールアドレスにサブスクリプションしていないか確認

```bash
# SNS トピックのサブスクリプション確認
aws sns list-subscriptions --region ap-northeast-1
```

#### 通知が受け取れない

1. 通知メール確認（迷惑メールフォルダ）
2. `notificationMode` が `'none'` になっていないか確認
3. SNS Topic のリソースポリシー確認

```bash
aws sns get-topic-attributes \
  --topic-arn arn:aws:sns:ap-northeast-1:123456789012:BLEAGovBaseCtDetectionAlarmTopic \
  --attribute-names Policy
```

## CloudFormation パラメータ

StackSet は以下のパラメータを CloudFormation テンプレートに渡します：

| パラメータ | 説明 | 例 |
|-----------|------|-----|
| `NotificationMode` | 通知モード | `centralized`, `regional`, `none` |
| `SecurityNotifyEmail` | 通知先メール | `security-ops@example.com` |
| `SecuritySlackWorkspaceId` | Slack Workspace ID | `TXXXXXXXXXX` |
| `SecuritySlackChannelId` | Slack Channel ID | `CXXXXXXXXXX` |
| `S3ExpirationDays` | S3 オブジェクト有効期間 | `366` |
| `S3ExpiredObjectDeleteDays` | S3 削除済みオブジェクト保持期間 | `30` |

## ベストプラクティス

1. **Centralized モード推奨**: 通知管理を一元化できます
2. **アラートフィルタリング**: SNS メッセージフィルタリング機能を使用してアラート量を調整
3. **タグ付け**: CloudWatch Alarms に `Region`, `Account` タグを付与して識別を容易に
4. **監視ダッシュボード**: 管理アカウント側で集約ダッシュボードを作成
5. **段階的ロールアウト**: 本番環境への展開前に、少数のアカウント/リージョンでテスト

## テスト

### 統合テスト

実際にデプロイして動作を確認する統合テストを提供しています。

#### 自動テスト（推奨）

デプロイから検証までを自動化したスクリプト：

```bash
# Linux/Mac
npm run test:deploy

# Windows (PowerShell)
npm run test:deploy:win
```

このスクリプトは以下を実行します：
1. 依存関係のインストール
2. parameter.ts の確認プロンプト
3. StackSet マネージャーのデプロイ
4. StackInstances 作成の待機（3分）
5. StackSet と StackInstances の状態確認
6. オプションでリソースのクリーンアップ

#### 手動テスト

1. **デプロイ**:
```bash
npx cdk deploy Dev-BLEAGovBaseCtStackSetManager
```

2. **検証**（デプロイ後3-5分待機）:
```bash
npm run test:integration
```

検証内容：
- ✅ StackSet の存在確認
- ✅ StackSet のステータス確認（ACTIVE）
- ✅ StackInstances の状態確認（全て CURRENT）

3. **クリーンアップ**:
```bash
npx cdk destroy Dev-BLEAGovBaseCtStackSetManager
```

## 024 の Stack 定義を更新する場合

1. 024ディレクトリで Stack 定義を変更（必要に応じて）
2. 039ディレクトリの `parameter.ts` を更新（必要に応じて）
3. `npx cdk deploy` を再実行

テンプレートは自動的に再生成され、StackSets が更新されます。

## ファイル詳細

| ファイル | 説明 |
|---------|------|
| [parameter.ts](parameter.ts) | StackSet デプロイパラメータ（通知モード、対象アカウント/リージョン） |
| [bin/blea-gov-base-ct-stacksets.ts](bin/blea-gov-base-ct-stacksets.ts) | CDK アプリケーションのエントリーポイント |
| [lib/stack/blea-gov-base-ct-stackset-manager-stack.ts](lib/stack/blea-gov-base-ct-stackset-manager-stack.ts) | StackSet マネージャースタックの実装 |
| [lib/construct/stackset-manager.ts](lib/construct/stackset-manager.ts) | StackSet 作成・管理の Construct |
| [lib/stage/blea-gov-base-ct-template-stage.ts](lib/stage/blea-gov-base-ct-template-stage.ts) | テンプレート生成用 Stage |

## 関連リンク

- [024.test-custom-blea-gov-base-ct](../024.test-custom-blea-gov-base-ct)
- [AWS CloudFormation StackSets ドキュメント](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/what-is-cfnstacksets.html)
- [AWS Control Tower](https://aws.amazon.com/controltower/)