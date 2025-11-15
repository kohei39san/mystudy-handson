# SCP EC2タグ付与強制

## 概要

このテンプレートは、AWS Organizations Service Control Policy (SCP) を使用してEC2インスタンスの作成時にタグ付与を強制するCloudFormationテンプレートです。

## 構成

### リソース
- **AWS Organizations Policy**: EC2インスタンス作成時のタグ付与を強制するSCPポリシー

### 対象リージョン
- ap-northeast-1 (東京リージョン)

## 機能

### タグ付与の強制
- EC2インスタンス (`RunInstances` アクション) の作成時に必須タグの付与を強制します
- 以下のタグが必須となります：
  - `Name`: インスタンス名
  - `Environment`: 環境名 (dev, staging, prod など)
  - `Owner`: 所有者情報

### 除外リソース
以下のリソースはタグ付与の強制対象外となります：
- Network Interface (NIC)
- EC2 Instance Connect Endpoint (EICE)
- Security Group
- Key Pair
- その他のEC2関連リソース

## ファイル構成

```
032.scp-ec2-tagging/
├── README.md                    # このファイル
├── cfn/
│   └── scp-ec2-tagging.yaml    # CloudFormationテンプレート
└── scripts/
    ├── deploy.sh               # デプロイスクリプト
    ├── cleanup.sh              # クリーンアップスクリプト
    ├── validate-template.sh    # テンプレート検証スクリプト
    ├── manage-policy.py        # ポリシー管理Pythonスクリプト
    └── help.sh                 # ヘルプスクリプト
```

## 使用方法

### 1. テンプレートの検証
```bash
cd /workspace/032.scp-ec2-tagging
./scripts/validate-template.sh
```

### 2. デプロイ
```bash
./scripts/deploy.sh
```

### 3. クリーンアップ
```bash
./scripts/cleanup.sh
```

### 4. ポリシー管理（Python）
```bash
# 組織単位の一覧表示
python3 ./scripts/manage-policy.py list-ous

# 特定のOUのアカウント一覧表示
python3 ./scripts/manage-policy.py list-accounts <OU_ID>

# ポリシーをOUにアタッチ
python3 ./scripts/manage-policy.py attach <OU_ID>

# ポリシーをOUからデタッチ
python3 ./scripts/manage-policy.py detach <OU_ID>

# ポリシーのアタッチ先一覧表示
python3 ./scripts/manage-policy.py list-targets

# ポリシー詳細表示
python3 ./scripts/manage-policy.py policy-details
```

### 5. ヘルプ
```bash
./scripts/help.sh
```

## 注意事項

1. **Organizations の管理アカウント**: このSCPは AWS Organizations の管理アカウントからのみデプロイ可能です
2. **既存リソースへの影響**: 既存のEC2インスタンスには影響しません。新規作成時のみ適用されます
3. **権限の確認**: デプロイ前に適切な Organizations 権限があることを確認してください
4. **テスト環境での検証**: 本番環境に適用する前に、テスト環境での動作確認を推奨します
5. **Python環境**: ポリシー管理スクリプトの使用にはPython 3とboto3ライブラリが必要です

## 必要な権限

### CloudFormation デプロイ用
- `organizations:CreatePolicy`
- `organizations:DescribePolicy`
- `cloudformation:CreateStack`
- `cloudformation:UpdateStack`
- `cloudformation:DeleteStack`
- `cloudformation:DescribeStacks`

### ポリシー管理用（Python スクリプト）
- `organizations:ListRoots`
- `organizations:ListOrganizationalUnitsForParent`
- `organizations:ListAccountsForParent`
- `organizations:AttachPolicy`
- `organizations:DetachPolicy`
- `organizations:ListTargetsForPolicy`

## トラブルシューティング

### よくある問題

1. **Organizations 権限不足**
   - 管理アカウントでの実行を確認
   - `organizations:CreatePolicy` 権限の確認

2. **ポリシーの適用範囲**
   - 対象となる組織単位 (OU) の確認
   - ポリシーのアタッチ状況の確認

3. **タグ要件の調整**
   - 必要に応じてテンプレート内のタグ要件をカスタマイズ

## 参考資料

- [AWS Organizations Service Control Policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)
- [EC2 タグベースのアクセス制御](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/control-access-with-tags.html)