# OCI Terraform State Bucket

Oracle Cloud Infrastructure (OCI) でTerraformのstateファイルを保存するためのObject Storage Bucketを作成するTerraform構成です。

## リソース構成

このTerraform構成では以下のリソースを作成します：

### Object Storage Bucket
- **名前**: 変数で指定可能（デフォルト: terraform-state-bucket）
- **バージョニング**: 有効
- **パブリックアクセス**: 無効（NoPublicAccess）
- **ストレージ階層**: Standard
- **オブジェクトイベント**: 無効
- **タグ**: Purpose = terraform-state

### データソース
- **Namespace**: コンパートメントのObject Storageネームスペースを取得

## ファイル構成

- `main.tf`: メインのリソース定義
- `variables.tf`: 入力変数の定義
- `outputs.tf`: 出力値の定義
- `terraform.tfvars.example`: 設定例ファイル

## 使用方法

[![Deploy to Oracle Cloud](https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg)](https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://github.com/kohei39san/mystudy-handson/raw/refs/heads/main/028.oci-bucket-tfstate/src/terraform-config.zip)

### 1. 設定ファイルの準備

```bash
cp terraform.tfvars.example terraform.tfvars
```

terraform.tfvarsファイルを編集して、適切な値を設定してください。

### 2. Terraformの実行

```bash
terraform init
terraform plan
terraform apply
```

### 3. Zipファイルの作成

OCI Resource Managerで使用するためのzipファイルを作成：

```powershell
# scriptsディレクトリに移動
cd scripts

# デフォルトのファイル名で作成
PowerShell -ExecutionPolicy RemoteSigned '.\create-terraform-zip.ps1'

# カスタムファイル名で作成
PowerShell -ExecutionPolicy RemoteSigned '.\create-terraform-zip.ps1 -OutputPath my-terraform-config.zip'
```

実行例：
```powershell
PS C:\mystudy-handson\028.oci-bucket-tfstate\scripts> .\create-terraform-zip.ps1
Created zip file: ../src/terraform-config.zip
Contains 4 .tf files:
  - main.tf
  - outputs.tf
  - terraform.tfvars.example
  - variables.tf
```

## 出力値

- `bucket_name`: 作成されたバケット名
- `bucket_namespace`: バケットのネームスペース
- `bucket_url`: バケットのURL

## 注意事項

- コンパートメントIDは必須パラメータです
- バケット名は一意である必要があります
- 適切なOCI認証情報が設定されている必要があります