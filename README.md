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