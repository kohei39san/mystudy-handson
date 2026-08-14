# AI opt-out policy + S3 パブリックアクセスブロック (Organizations S3 Policy)

## 概要

本ディレクトリは、AWS Organizations の **AIオプトアウトポリシー** および **Organizations S3 ポリシー（パブリックアクセスブロック）** を、単一の CloudFormation スタックで管理するハンズオン構成です。

S3 ポリシーは個別バケットへの `AWS::S3::BucketPolicy` ではなく、**Organizations S3 Policy**（`Type: S3_POLICY`）として組織・OU・アカウント単位のガードレールとして適用します。バケット名の指定は不要で、アタッチ先配下のすべての S3 バケットに一括適用されます。

| リソース | 用途 |
|---|---|
| `AWS::Organizations::Policy` (AISERVICES_OPT_OUT_POLICY) | 生成AI関連サービスへのデータ利用オプトアウトポリシーを作成・アタッチ |
| `AWS::Organizations::Policy` (S3_POLICY) | 組織・OU・アカウント配下の全バケットに対してパブリックアクセスブロック（4設定すべて有効）をガードレールとして適用 |

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
| `AiOptOutPolicyName` | ✅ | `ai-optout-policy` | AI オプトアウト Organizations ポリシーのベース名（末尾に `-{Env}` が付与される） |
| `TargetIds` | ❌ | `""` | 両ポリシーのアタッチ先（OU ID または アカウント ID、カンマ区切り）。空の場合はポリシー作成のみ |
| `AiOptOutPolicyDocument` | ✅ | 全サービスオプトアウト JSON | Organizations AI opt-out ポリシー JSON 文字列 |
| `S3PolicyName` | ✅ | `s3-public-access-block-policy` | Organizations S3 ポリシーのベース名（末尾に `-{Env}` が付与される） |
| `S3OrgPolicyDocument` | ✅ | パブリックアクセスブロック全有効 JSON | Organizations S3 ポリシー JSON 文字列（デフォルトで4つのパブリックアクセスブロック設定をすべて有効化） |

> **注意**: `TargetIds` は内部情報です。パラメータファイル (`parameters/*.json`) への平文コミットを避け、必要に応じて SSM Parameter Store / Secrets Manager から注入してください。

## 前提条件

- **デプロイアカウント**: AWS Organizations の**管理アカウント**
- **IAM 権限** (CloudFormation 実行ロールに付与すること):

  | サービス | 必要な権限 |
  |---|---|
  | Organizations | `organizations:CreatePolicy`, `organizations:UpdatePolicy`, `organizations:AttachPolicy`, `organizations:List*`, `organizations:Describe*` |
  | CloudFormation | `cloudformation:CreateStack`, `cloudformation:UpdateStack`, `cloudformation:DescribeStacks` など |

- **Organizations ポリシータイプの有効化**: 管理アカウントで両ポリシータイプが有効になっていること
  ```bash
  ROOT_ID=$(aws organizations list-roots --query 'Roots[0].Id' --output text)

  aws organizations enable-policy-type \
    --root-id "$ROOT_ID" \
    --policy-type AISERVICES_OPT_OUT_POLICY

  aws organizations enable-policy-type \
    --root-id "$ROOT_ID" \
    --policy-type S3_POLICY
  ```

## デプロイ手順

### 1. TargetIds を確認する

```bash
# OU ID の確認
aws organizations list-organizational-units-for-parent \
  --parent-id $(aws organizations list-roots --query 'Roots[0].Id' --output text)

# アカウント ID の確認
aws sts get-caller-identity --query Account --output text
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
  --parameter-overrides "TargetIds=<OU_ID_OR_ACCOUNT_ID>" \
  --change-set-name review-$(date +%Y%m%d%H%M%S) \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation describe-change-set \
  --stack-name ai-optout-s3-policy-dev \
  --change-set-name review-<TIMESTAMP>
```

### 4. デプロイする（dev 環境）

```bash
aws cloudformation deploy \
  --stack-name ai-optout-s3-policy-dev \
  --template-file cfn/infrastructure.yaml \
  --parameter-overrides file://cfn/parameters/dev.json "TargetIds=<OU_ID_OR_ACCOUNT_ID>" \
  --capabilities CAPABILITY_NAMED_IAM
```

> 複数の OU / アカウントを指定する場合はカンマ区切りにします:
> ```
> "TargetIds=ou-xxxx-yyyyyyyy,123456789012"
> ```

### 5. prod 環境へ展開する（dev 検証完了後）

```bash
aws cloudformation deploy \
  --stack-name ai-optout-s3-policy-prod \
  --template-file cfn/infrastructure.yaml \
  --parameter-overrides file://cfn/parameters/prod.json "TargetIds=<OU_ID_OR_ACCOUNT_ID>" \
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
  --filter AISERVICES_OPT_OUT_POLICY
```

期待結果: `target-id` に対して意図したポリシー ID が返ること。

### Organizations S3 ポリシー（パブリックアクセスブロック）の確認

```bash
# スタック出力からポリシー ID を取得
S3_POLICY_ID=$(aws cloudformation describe-stacks \
  --stack-name ai-optout-s3-policy-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`S3OrgPolicyId`].OutputValue' \
  --output text)

# ポリシー詳細の確認
aws organizations describe-policy --policy-id "$S3_POLICY_ID"

# 対象 OU/アカウントへのアタッチ確認
aws organizations list-policies-for-target \
  --target-id <ou-or-account-id> \
  --filter S3_POLICY
```

期待結果: `target-id` に対して意図したポリシー ID が返り、`public_access_block_configuration` の設定がすべて有効になっていることが確認できること。

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

### ポリシーのデタッチ（手動）

```bash
aws organizations detach-policy \
  --policy-id <policy-id> \
  --target-id <ou-or-account-id>
```

## セキュリティ設計

| 観点 | 内容 |
|---|---|
| パブリックアクセスブロック | Organizations S3 ポリシーで4つのパブリックアクセスブロック設定（BlockPublicAcls, BlockPublicPolicy, IgnorePublicAcls, RestrictPublicBuckets）を組織・OU・アカウント単位のガードレールとして有効化 |
| AIデータ利用オプトアウト | Organizations AIオプトアウトポリシーで全 AI サービスをデフォルトオプトアウト |
| シークレット管理 | アカウント ID・OU ID は SSM Parameter Store / Secrets Manager から注入推奨 |
| 最小権限 | CloudFormation 実行ロールは Organizations の最小権限に絞ること |

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
- [AWS Organizations S3 policy syntax and examples](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_s3_syntax.html)
- [AWS Organizations S3 policy 公式ドキュメント](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_s3.html)
- [AWS::Organizations::Policy CloudFormation リファレンス](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-organizations-policy.html)

