# GitHub Actions OIDC プロバイダーセットアップ

このCloudFormationテンプレートは以下のリソースを作成します：
- GitHub Actions用のOIDCプロバイダー
- 指定したGitHubリポジトリからのみ利用可能なPowerUserAccessポリシーを持つIAMロール

## デプロイ方法

AWS CLIを使用して以下のようにスタックをデプロイします：

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name github-oidc-provider \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    GitHubRepository=組織名/リポジトリ名
```

`組織名/リポジトリ名` は、あなたのGitHubリポジトリの情報に置き換えてください。
例：`repo:<GitHub username>/<GitHub repository name>:ref:refs/heads/<branch name>`

## GitHub Actionsでの利用方法

デプロイ後、以下のようにGitHub Actionsワークフローでロールを使用できます：

```yaml
jobs:
  deploy:
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: aws-actions/configure-aws-credentials@v1
        with:
          role-to-assume: ${{ env.ROLE_ARN }}
          aws-region: ap-northeast-1
```

作成されたロールのARNは、CloudFormationスタックの出力から確認できます。
