# SCP & Tag Policy - Owner Tag Enforcement

このCloudFormationテンプレート群は、特定のAWSリソースを作成する際に`Owner`タグの指定を強制するService Control Policy (SCP)と、タグの形式を制御するTag Policyをデプロイします。

## 概要

このSCPは、以下のリソースを作成する際に`Owner`タグが指定されていない場合、そのアクションを拒否します：

- Athena WorkGroup
- CloudTrail Trail
- CloudWatch Metric Alarm
- EC2インスタンス、EIP、NATゲートウェイ、スナップショット、ボリューム、VPCエンドポイント
- ECSクラスター、サービス
- EFS、FSx ファイルシステム
- EKSクラスター
- OpenSearch/Elasticsearch ドメイン
- KMSキー
- OpenSearch Serverless コレクション
- RDS インスタンス
- Secrets Manager シークレット

## 前提条件

- AWS Organizationsが有効化されていること
- CloudFormationを実行するアカウントが組織の管理アカウントであること
- SCPを有効化していること

## テンプレート一覧

### cfnディレクトリ内のテンプレート

1. **scp-template.yaml** - Service Control Policy（リソース作成時のOwnerタグ必須化）
2. **tag-policy-template.yaml** - Tag Policy（Ownerタグの値を@example.com形式に制限）

## デプロイ方法

### 1. SCPをデプロイ

```bash
# ポリシーのみ作成（アタッチなし）
aws cloudformation create-stack \
  --stack-name scp-owner-tag-enforcement \
  --template-body file://cfn/scp-template.yaml \
  --parameters file://src/scp-parameters.json

# 特定のOUまたはアカウントにアタッチしてデプロイ
aws cloudformation create-stack \
  --stack-name scp-owner-tag-enforcement \
  --template-body file://cfn/scp-template.yaml \
  --parameters \
    ParameterKey=PolicyName,ParameterValue=EnforceOwnerTagPolicy \
    ParameterKey=PolicyDescription,ParameterValue="Deny resource creation without Owner tag" \
    ParameterKey=TargetIds,ParameterValue="ou-xxxx-xxxxxxxx"
```

### 2. Tag Policyをデプロイ

```bash
# ポリシーのみ作成（アタッチなし）
aws cloudformation create-stack \
  --stack-name tag-policy-owner-enforcement \
  --template-body file://cfn/tag-policy-template.yaml \
  --parameters file://src/tag-policy-parameters.json

# 特定のOUまたはアカウントにアタッチしてデプロイ
aws cloudformation create-stack \
  --stack-name tag-policy-owner-enforcement \
  --template-body file://cfn/tag-policy-template.yaml \
  --parameters \
    ParameterKey=PolicyName,ParameterValue=OwnerTagPolicy \
    ParameterKey=PolicyDescription,ParameterValue="Enforce Owner tag with @example.com email format" \
    ParameterKey=TargetIds,ParameterValue="ou-xxxx-xxxxxxxx"
```

### 3. スクリプトを使用したデプロイ

```bash
cd scripts

# SCPをデプロイ
./deploy-scp.sh deploy
./deploy-scp.sh deploy ou-xxxx-xxxxxxxx

# Tag Policyをデプロイ
./deploy-tag-policy.sh deploy
./deploy-tag-policy.sh deploy ou-xxxx-xxxxxxxx
```

## パラメータ

### SCPテンプレート

| パラメータ名 | 説明 | デフォルト値 |
|------------|------|-------------|
| PolicyName | SCPポリシーの名前 | EnforceOwnerTagPolicy |
| PolicyDescription | SCPポリシーの説明 | Deny resource creation without Owner tag |
| TargetIds | ポリシーをアタッチするOU IDまたはアカウントIDのカンマ区切りリスト | (空) |

### Tag Policyテンプレート

| パラメータ名 | 説明 | デフォルト値 |
|------------|------|-------------|
| PolicyName | Tag Policyの名前 | OwnerTagPolicy |
| PolicyDescription | Tag Policyの説明 | Enforce Owner tag with @example.com email format |

# Tag Policyをデプロイ
./deploy-tag-policy.sh deploy
./deploy-tag-policy.sh deploy ou-xxxx-xxxxxxxx
### SCPテンプレート

| 出力名 | 説明 |
|-------|------|
| PolicyId | SCPの一意識別子 |
| PolicyArn | SCPのARN |

### Tag Policyテンプレート

| 出力名 | 説明 |
|-------|------|
| PolicyId | Tag Policyの一意識別子 |
| PolicyArn | Tag Policy
| パラメータ名 | 説明 | デフォルト値 |
|------------|------|-------------|
| PolicyName | SCPポリシーの名前 | EnforceOwnerTagPolicy |
| PolicyDescription | SCPポリシーの説明 | Deny resource creation without Owner tag |
| TargetIds | ポリシーをアタッチするOU IDまたはアカウントIDのカンマ区切りリスト | (空) |

## 出力

| 出力名 | 説明 |
|-------|------|
| PolicyId | SCPの一意識別子 |
| PolicyArn | SCPのARN |

## 使用例

### Ownerタグを指定してEC2インスタンスを起動（成功）

```bash
aws ec2 run-instances \
  --image-id ami-xxxxxxxxx \
  --instance-type t3.micro \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Owner,Value=user@example.com}]'
```Tag Policyについて

Tag Policyは、組織内のリソースに適用されるタグの値を制御します：

- `Owner`タグの値が`*@example.com`形式（会社のメールアドレス）に準拠する必要があります
- 広範囲のAWSリソースに対してタグポリシーが適用されます
- SCPと組み合わせることで、タグの存在と形式の両方を強制できます

## 参考資料

- [AWS Organizations - Service Control Policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)
- [AWS Organizations - Tag Policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_tag-policie

```bash
aws ec2 run-instances \
  --image-id ami-xxxxxxxxx \
  --instance-type t3.micro
# エラー: Access Denied by Service Control Policy
```

##SCPスタックを削除
aws cloudformation delete-stack --stack-name scp-owner-tag-enforcement

# Tag Policyスタックを削除
aws cloudformation delete-stack --stack-name tag-policy-owner-enforcement

# または、スクリプトを使用
cd scripts
./deploy-scp.sh delete
./deploy-tag-policy.sh delete
- SCPは組織の管理アカウントには適用されません
- ポリシーを変更する場合は、影響範囲を十分に確認してください
- 既存のリソースには影響しません（新規作成時のみ適用）

## クリーンアップ

```bash
# ポリシーをデタッチしてからスタックを削除
aws cloudformation delete-stack --stack-name scp-owner-tag-enforcement
```

## 参考資料

- [AWS Organizations - Service Control Policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)
- [CloudFormation - AWS::Organizations::Policy](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-organizations-policy.html)
