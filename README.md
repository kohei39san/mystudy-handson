[![CodeQL Advanced](https://github.com/kohei39san/mystudy-handson/actions/workflows/codeql.yml/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/codeql.yml)
[![Terraform linter and PR](https://github.com/kohei39san/mystudy-handson/actions/workflows/terraform-linter-pr.yml/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/terraform-linter-pr.yml)
[![Dependabot Updates](https://github.com/kohei39san/mystudy-handson/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/dependabot/dependabot-updates)
[![CloudFormation Linter](https://github.com/kohei39san/mystudy-handson/actions/workflows/cfn-lint.yml/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/cfn-lint.yml)
[![GitHub Actions Linter](https://github.com/kohei39san/mystudy-handson/actions/workflows/github-actions-linter.yml/badge.svg)](https://github.com/kohei39san/mystudy-handson/actions/workflows/github-actions-linter.yml)

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

## 週次README更新ワークフロー

このリポジトリには、週次でREADME.mdファイルの最新化を行うためのGitHub Actionsワークフローが含まれています。

### 機能概要

- 毎週月曜日の午前9時(UTC)に自動実行されます
- リポジトリ内のREADME.mdファイルを最新化するためのIssueを作成します
- 作成されたIssueには「Amazon Q development agent」ラベルが自動的に付与されます
- Amazon Qがラベルを検知し、README.mdの更新作業を自動的に開始します

### 設定方法

1. リポジトリの環境変数に`README_UPDATE_PROMPT`を設定することで、カスタムプロンプトを指定できます
2. 環境変数が設定されていない場合は、デフォルトのプロンプトが使用されます

### 手動実行

1. GitHubのActionsタブから「Weekly README Update」ワークフローを選択します
2. 「Run workflow」をクリックして手動で実行することもできます

## GitHub Actions YAMLファイルのLinter

このリポジトリには、GitHub ActionsのYAMLファイルを自動的にlintするためのワークフローが含まれています。

### 機能概要

- リポジトリ内のGitHub Actions YAMLファイル（`.github/workflows/*.yml`）の構文チェックを行います
- すべてのブランチへのプッシュ時に自動的に実行されます
- GitHub Actions YAMLファイル以外はlintの対象外です

### 使用されているツール

- [github/super-linter](https://github.com/github/super-linter): GitHubが提供する多言語対応のlintツール
  - YAML構文チェック
  - GitHub Actionsワークフロー構文チェック

### 注意事項

- このlinterはGitHub Actions YAMLファイルのみを対象としています
- 他のYAMLファイルはチェック対象外です

## 所有する別リポジトリへプッシュするワークフロー

このリポジトリには、コンテンツを別のリポジトリにプッシュするためのGitHub Actionsワークフローが含まれています。

### 機能概要

- メインブランチの内容を指定した別リポジトリにプッシュします
- プッシュ先リポジトリに新しいブランチを作成します
- プッシュ後、プッシュ先リポジトリのmainブランチに対するプルリクエストを自動作成します
- セキュリティのため、プッシュ先リポジトリは同じ所有者のリポジトリに限定されます

### 必要な設定

1. GitHub Secretsに以下の値を設定してください：
   - `TARGET_REPO_PAT`: プッシュ先リポジトリにアクセスするためのPersonal Access Token
   - `TARGET_REPO`: プッシュ先リポジトリ名（例: `owner/repo-name`）

### 使用方法

1. GitHubのActionsタブから「Push to Another Repository」ワークフローを選択します
2. 「Run workflow」をクリックし、以下の情報を入力します：
   - `Branch name to create in target repository`: 作成するブランチ名
   - `Commit message`: コミットメッセージ
   - `Pull request title`: プルリクエストのタイトル
   - `Pull request body`: プルリクエストの説明文
3. 「Run workflow」をクリックして実行を開始します

### 注意事項

- プッシュ先リポジトリは同じGitHubアカウント/組織が所有している必要があります
- 適切な権限を持つPersonal Access Tokenが必要です（repo権限を推奨）
- ワークフローは手動実行のみ可能です

## 前提条件

GitHub Actionsを使用するには、先にAWS側でOIDC認証のための設定が必要です。以下の手順で設定してください：

1. `013.aws-github-oidc/template.yaml`のCloudFormationテンプレートをデプロイします。
   * このテンプレートは以下のリソースを作成します：
     - GitHub Actions用のOIDCプロバイダー
     - GitHub Actionsが利用するIAMロール（PowerUserAccess権限付き）
   * デプロイ時にパラメータ`GitHubRepository`の指定が必要です
     - 形式: `repo:ユーザー名/リポジトリ名:ref:refs/heads/ブランチ名`
     - 例: `repo:example/mystudy-handson:ref:refs/heads/main`
     - 例: `repo:example/mystudy-handson:ref:refs/heads/*`

```powershell
> cd .\scripts\013.aws-github-oidc\
> PowerShell -ExecutionPolicy RemoteSigned './create-aws-oidc-provider.ps1 <stack-name> "組織名/リポジトリ名"'
```

`組織名/リポジトリ名` は、あなたのGitHubリポジトリの情報に置き換えてください。
例：`repo:<GitHub username>/<GitHub repository name>:ref:refs/heads/<branch name>`

2. デプロイ完了後、GitHub CLIをインストールし、`gh auth login`で認証を完了してください。

3. リポジトリの設定スクリプトを参考にGitHub Actions用の各種設定を行います：
```bat
scripts\setup-repository-for-github-actions.ps1
```
このスクリプトは以下の設定を行います：
* GitHub Actionsの権限設定
* 必要なSecrets（GEMINI_API_KEY, LLM_API_KEY, LLM_BASE_URL, PAT_TOKEN, PAT_USERNAME）の設定
* 必要なVariables（LLM_MODEL）の設定

## 実行手順

リポジトリにはTerraformを実行するためのGitHub Actionsワークフローが用意されています。
以下の手順で実行できます：

1. GitHubのActionsタブから「Terraform Apply Manual Test」ワークフローを選択します。

2. 「Run workflow」をクリックし、以下の情報を入力します：
   * `Directory number`: 実行するTerraformディレクトリの番号
     * 例: `001` (001.ec2-ec2,ec2ディレクトリを指定する場合)

注: ワークフローは実行時に選択されているブランチ上で実行されます。

3. 「Run workflow」をクリックして実行を開始します。

ワークフローは以下の順序で実行されます：
1. 現在のブランチをチェックアウト
2. 指定された番号のディレクトリを特定
3. terraform init
4. terraform plan
5. terraform apply
6. terraform destroy

注意事項：
* initまたはplanが失敗した場合、以降の処理は実行されません
* applyが失敗した場合でもdestroyは実行されます（ただしワークフロー自体は失敗として終了）
* 手動実行のみ可能です
