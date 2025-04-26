# 概要

勉強で使った基盤はEC2とTerraformで作りました。
使い方を記載します。

# フォルダ構成

* xxx(数字).yyy: 検証に応じたTerraformファイルが入っています。
* scripts: 検証で使用したスクリプトを格納しています。
* docs: 検証のメモを格納しています。
* src: terraform以外のマニフェストファイルを格納しています。
* wsl-old: 過去WSL環境で使用したソースファイルを格納しています

# 使い方

1. リポジトリをクローンします。
2. AWS CLIを使うための認証の設定ができていることを確認します。

* PowerShellにてSSO認証を行う場合には以下のような設定ファイルを作成する

```conf:C:\Users\user\.aws\config
[profile default]
sso_start_url = <sso-start-url>
sso_region = <sso-region>
sso_account_id = <sso-account-id>
sso_role_name = <sso-account-id>
region = <region>
output = json
```

3. Terraform CLIにてデプロイします。パラメータは適宜Overrideなどで変更してください。

* PowerShellの場合の例(defaultプロファイルを使用)

```
# cd mystudy-handson\001.ec2-ec2,ec2
# PowerShell -ExecutionPolicy RemoteSigned '..\scripts\aws-cli-source.ps1 default'
# terraform init
# terraform plan
# terraform apply
```

# GitHub Actionsによる実行方法

## 前提条件

GitHub Actionsを使用するには、先にAWS側でOIDC認証のための設定が必要です。以下の手順で設定してください：

1. `013.aws-github-oidc/template.yaml`のCloudFormationテンプレートをデプロイします。
   * このテンプレートは以下のリソースを作成します：
     - GitHub Actions用のOIDCプロバイダー
     - GitHub Actionsが利用するIAMロール（PowerUserAccess権限付き）
   * デプロイ時にパラメータ`GitHubRepository`の指定が必要です
     - 形式: `repo:ユーザー名/リポジトリ名:ref:refs/heads/ブランチ名`
     - 例: `repo:example/mystudy-handson:ref:refs/heads/main`

2. デプロイ完了後、出力される`RoleARN`をコピーしてGitHubのSecretsに設定します。

## 実行手順

リポジトリにはTerraformを実行するためのGitHub Actionsワークフローが用意されています。
以下の手順で実行できます：

1. リポジトリのSecretsに以下を設定します：
   * `AWS_ROLE_ARN`: GitHub ActionsがAWSリソースにアクセスするために使用するIAMロールのARN

2. GitHubのActionsタブから「Terraform Apply Manual Test」ワークフローを選択します。

3. 「Run workflow」をクリックし、以下の情報を入力します：
   * `Branch`: 実行するTerraformコードが存在するブランチ名（デフォルト: main）
   * `Directory containing Terraform files`: Terraformファイルが存在するディレクトリパス
     * 例: `001.ec2-ec2,ec2`

4. 「Run workflow」をクリックして実行を開始します。

ワークフローは以下の順序で実行されます：
1. 指定されたブランチをチェックアウト
2. terraform init
3. terraform plan
4. terraform apply
5. terraform destroy

注意事項：
* initまたはplanが失敗した場合、以降の処理は実行されません
* applyが失敗した場合でもdestroyは実行されます（ただしワークフロー自体は失敗として終了）
* 手動実行のみ可能です
