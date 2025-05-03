# GitHub Actions OIDC プロバイダーセットアップ

このCloudFormationテンプレートは以下のリソースを作成します：
- GitHub Actions用のOIDCプロバイダー
- 指定したGitHubリポジトリからのみ利用可能なPowerUserAccessポリシーを持つIAMロール

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
