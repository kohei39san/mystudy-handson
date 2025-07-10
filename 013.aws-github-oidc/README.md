# GitHub Actions OIDC プロバイダーセットアップ

このCloudFormationテンプレートは以下のリソースを作成します：
- GitHub Actions用のOIDCプロバイダー
  - URL: https://token.actions.githubusercontent.com
  - クライアントID: sts.amazonaws.com
  - サムプリント: 6938fd4d98bab03faadb97b34396831e3780aea1
- 指定したGitHubリポジトリからのみ利用可能なIAMロール
  - 付与されるポリシー: PowerUserAccess, IAMFullAccess
  - 信頼ポリシー: 指定されたGitHubリポジトリからのみAssumeRoleWithWebIdentityを許可

## パラメータ

- **GitHubRepository**: GitHub リポジトリの指定形式
  - 形式: `repo:<GitHub username>/<GitHub repository name>:ref:refs/heads/<branch name>`
  - 例: `repo:example/mystudy-handson:ref:refs/heads/main`
  - 例: `repo:example/mystudy-handson:ref:refs/heads/*` (すべてのブランチを許可)

## 出力

- **RoleARN**: 作成されたIAMロールのARN
  - GitHub Actionsワークフローで使用するためのロールARN

## デプロイ方法

../README.mdを参照してください

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
