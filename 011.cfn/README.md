# CloudFormation テンプレート集

## 概要

このディレクトリには、AWS CloudFormation テンプレートのサンプルが含まれています。これらのテンプレートを使用して、AWSリソースをコード化して管理することができます。

## テンプレート構成

### sample.yaml

このテンプレートは以下のリソースを作成します：

- **VPC**:
  - CIDR ブロック: 10.0.0.0/16

- **EC2インスタンス**:
  - AMI ID: ami-0c55b159cbfafe1f0
  - インスタンスタイプ: t2.micro
  - キーペア: my-key-pair
  - セキュリティグループ: MySecurityGroup

- **キーペア**:
  - 名前: my-key-pair

- **セキュリティグループ**:
  - 説明: My security group
  - VPC: MyVPC

### sample2/sample2.yaml

このテンプレートは以下のリソースを作成します：

- **VPC**:
  - CIDR ブロック: 10.0.0.0/16

- **EC2インスタンス**:
  - AMI ID: ami-0c55b159cbfafe1f0
  - インスタンスタイプ: t2.micro
  - キーペア: my-key-pair
  - セキュリティグループ: MySecurityGroup

- **キーペア**:
  - 名前: my-key-pair

- **セキュリティグループ**:
  - 説明: My security group
  - VPC: MyVPC
  - インバウンドルール: SSH (ポート22) を任意の場所から許可

- **出力**:
  - EC2インスタンスのパブリックDNS名

## 使用方法

メインのREADME.mdに記載されている手順に従って、これらのテンプレートをデプロイしてください。

```bash
# AWS CLIを使用してテンプレートをデプロイする例
aws cloudformation deploy --template-file cfn/sample.yaml --stack-name my-sample-stack
```

## 注意事項

- これらのテンプレートはサンプルであり、本番環境での使用前にセキュリティ設定を見直してください。
- セキュリティグループの設定は、必要に応じて制限してください。
- キーペアは適切に管理してください。