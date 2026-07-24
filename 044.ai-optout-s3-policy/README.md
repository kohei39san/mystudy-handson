# AI opt-out policy + S3 TLS enforcement

## 概要

本ディレクトリは、AWS Organizations の **AIオプトアウトポリシー** および Amazon S3 の **TLS強制バケットポリシー** を、単一の CloudFormation スタックで管理するハンズオン構成です。

| リソース | 用途 |
|---|---|
| `AWS::Organizations::Policy` (AISERVICES_OPT_OUT_POLICY) | 生成AI関連サービスへのデータ利用オプトアウトポリシーを作成・アタッチ |
| `AWS::S3::BucketPolicy` | 対象バケットに TLS 強制 Deny ポリシーを適用 |

## ファイル構成

```
044.ai-optout-s3-policy/
├── cfn/
│   ├── infrastructure.yaml        # CloudFormation テンプレート（単一スタック）
│   └── parameters/
│       ├── dev.json               # dev 環境向けパラメータ
│       └── prod.json              # prod 環境向けパラメータ
├── src/                           # アーキテクチャ図など
└── README.md                      # このファイル
```

## パラメータ一覧

| パラメータ名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| `Env` | ✅ | `dev` | デプロイ環境 (`dev` / `staging` / `prod`) |
| `Owner` | ✅ | `platform-team` | リソースの所有者 |
| `Project` | ✅ | `security-governance` | プロジェクト名 |
| `CostCenter` | ❌ | `""` | コスト配賦コード |
| `AiOptOutPolicyName` | ✅ | `ai-optout-policy` | Organizations ポリシーのベース名（末尾に `-{Env}` が付与される） |
| `TargetIds` | ❌ | `""` | AI ポリシーのアタッチ先（OU ID または アカウント ID、カンマ区切り）。空の場合はポリシー作成のみ |
| `AiOptOutPolicyDocument` | ✅ | 全サービスオプトアウト JSON | Organizations AI opt-out ポリシー JSON 文字列 |
| `TargetBucketName` | ❌ | `""` | TLS 強制を適用するバケット名 (1つ目) |
| `TargetBucketName2` | ❌ | `""` | TLS 強制を適用するバケット名 (2つ目) |
| `TargetBucketName3` | ❌ | `""` | TLS 強制を適用するバケット名 (3つ目) |
| `EnforceTlsOnly` | ✅ | `true` | `true` の場合、各バケットに TLS 強制 Deny ステートメントを適用 |

> **注意**: `TargetIds`・`TargetBucketName*` は内部情報です。パラメータファイル (`parameters/*.json`) への平文コミットを避け、必要に応じて SSM Parameter Store / Secrets Manager から注入してください。

## 前提条件

- **デプロイアカウント**: AWS Organizations の**管理アカウント**（AIオプトアウトポリシーの作成に必要）
- **IAM 権限** (CloudFormation 実行ロールに付与すること):

  | サービス | 必要な権限 |
  |---|---|
  | Organizations | `organizations:CreatePolicy`, `organizations:UpdatePolicy`, `organizations:AttachPolicy`, `organizations:List*`, `organizations:Describe*` |
  | S3 | `s3:GetBucketPolicy`, `s3:PutBucketPolicy` |
  | CloudFormation | `cloudformation:CreateStack`, `cloudformation:UpdateStack`, `cloudformation:DescribeStacks` など |

- **Organizations ポリシータイプの有効化**: 管理アカウントで AISERVICES_OPT_OUT_POLICY が有効になっていること
  ```bash
  aws organizations enable-policy-type \
    --root-id $(aws organizations list-roots --query 'Roots[0].Id' --output text) \
    --policy-type AISERVICES_OPT_OUT_POLICY
  ```

## デプロイ手順

### 1. パラメータを設定する

`cfn/parameters/dev.json` を編集し、`REPLACE_WITH_*` プレースホルダを実際の値に置き換えます。

```bash
# 例: OU ID の確認
aws organizations list-organizational-units-for-parent \
  --parent-id $(aws organizations list-roots --query 'Roots[0].Id' --output text)

# 例: バケット名の確認
aws s3 ls
```

### 2. テンプレートを静的検証する

```bash
cd 044.ai-optout-s3-policy
cfn-lint cfn/infrastructure.yaml
```

### 3. Change Set で差分を確認する

```bash
aws cloudformation create-change-set \
  --stack-name ai-optout-s3-policy-dev \
  --template-body file://cfn/infrastructure.yaml \
  --parameters file://cfn/parameters/dev.json \
  --change-set-name review-$(date +%Y%m%d%H%M%S) \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation describe-change-set \
  --stack-name ai-optout-s3-policy-dev \
  --change-set-name review-<TIMESTAMP>
```

### 4. デプロイする

```bash
aws cloudformation deploy \
  --stack-name ai-optout-s3-policy-dev \
  --template-file cfn/infrastructure.yaml \
  --parameter-overrides file://cfn/parameters/dev.json \
  --capabilities CAPABILITY_NAMED_IAM
```

### 5. prod 環境へ展開する（dev 検証完了後）

```bash
aws cloudformation deploy \
  --stack-name ai-optout-s3-policy-prod \
  --template-file cfn/infrastructure.yaml \
  --parameter-overrides file://cfn/parameters/prod.json \
  --capabilities CAPABILITY_NAMED_IAM
```

## 検証手順

### AIオプトアウトポリシーの確認

```bash
# スタック出力からポリシー ID を取得
POLICY_ID=$(aws cloudformation describe-stacks \
  --stack-name ai-optout-s3-policy-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`AIOptOutPolicyId`].OutputValue' \
  --output text)

# ポリシー詳細の確認
aws organizations describe-policy --policy-id "$POLICY_ID"

# 対象 OU/アカウントへのアタッチ確認
aws organizations list-policies-for-target \
  --target-id <ou-or-account-id> \
  --filter AI_SERVICES_OPT_OUT_POLICY
```

期待結果: `target-id` に対して意図したポリシー ID が返ること。

### S3 バケットポリシーの確認

```bash
# バケットポリシーの確認
aws s3api get-bucket-policy \
  --bucket <bucket-name> \
  --query Policy \
  --output text | python3 -m json.tool

# TLS 強制 Deny ステートメントが含まれることを確認
aws s3api get-bucket-policy \
  --bucket <bucket-name> \
  --query Policy \
  --output text | python3 -c "
import json, sys
policy = json.load(sys.stdin)
for stmt in policy['Statement']:
    cond = stmt.get('Condition', {}).get('Bool', {})
    if cond.get('aws:SecureTransport') == 'false' and stmt['Effect'] == 'Deny':
        print('TLS enforcement found:', stmt['Sid'])
"
```

期待結果: `TLS enforcement found: DenyNonTLS` が出力されること。

## ロールバック手順

### CloudFormation スタックのロールバック

```bash
# スタックを削除してリソースをすべて削除
aws cloudformation delete-stack --stack-name ai-optout-s3-policy-dev

# 特定バージョンに戻す場合: 直前の安定コミットへロールバックし再デプロイ
git checkout <stable-commit-hash> -- 044.ai-optout-s3-policy/cfn/infrastructure.yaml
aws cloudformation deploy \
  --stack-name ai-optout-s3-policy-dev \
  --template-file cfn/infrastructure.yaml \
  --parameter-overrides file://cfn/parameters/dev.json \
  --capabilities CAPABILITY_NAMED_IAM
```

### AI ポリシーのデタッチ（手動）

```bash
aws organizations detach-policy \
  --policy-id <policy-id> \
  --target-id <ou-or-account-id>
```

### S3 バケットポリシーの削除（手動）

```bash
aws s3api delete-bucket-policy --bucket <bucket-name>
```

## セキュリティ設計

| 観点 | 内容 |
|---|---|
| TLS 強制 | `aws:SecureTransport = false` のリクエストをすべて Deny |
| AIデータ利用オプトアウト | Organizations AIオプトアウトポリシーで全 AI サービスをデフォルトオプトアウト |
| シークレット管理 | アカウント ID・OU ID・バケット名は SSM Parameter Store / Secrets Manager から注入推奨 |
| 最小権限 | CloudFormation 実行ロールは Organizations と S3 の最小権限に絞ること |

## タグ設計

| タグキー | 値 |
|---|---|
| `Name` | `ai-optout-and-s3-policy` |
| `Env` | `dev` / `staging` / `prod` |
| `Owner` | `platform-team` |
| `Project` | `security-governance` |
| `CostCenter` | コスト配賦コード（任意） |

## 参考資料

- [AWS Organizations AI services opt-out policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_ai-opt-out.html)
- [AWS::Organizations::Policy CloudFormation リファレンス](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-organizations-policy.html)
- [AWS::S3::BucketPolicy CloudFormation リファレンス](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-s3-bucketpolicy.html)
- [Amazon S3 バケットポリシー例 – aws:SecureTransport](https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html)
