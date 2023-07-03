# 概要

勉強で使った基盤はEC2とTerraformで作りました。このディレクトリではTerraformで使用したファイルを配置し、使い方について記載します。

# フォルダ構成

* tf-manifests/common: 各基盤で共通の要素を定義しています。
* tf-manifests/k0s: シングルノードでk0sを構築する設定を定義しています。（参考：https://k0sproject.io/）
* scripts: DockerやKubernetesをインストールするためのスクリプトが入っています。

# 使い方

1. リポジトリをクローンします。
2. AWS CLIを使うための認証の設定ができていることを確認します。
3. Terraform CLIにてデプロイします。パラメータは適宜Overrideなどで変更してください。

```
# Ex. deploy k0s
$ cd tf-manifests/k0s
$ terraform init
$ terraform plan
$ terraform apply
```

# Overrideの例

## EC2のSSHログインに用いる鍵の設定

以下のようなファイルを作成する。

tf-manifests/common/override.tf

```
variable "instance_public_key" {
  type    = string
  default = "/path/to/public_key"
}

variable "instance_private_key" {
  type    = string
  default = "/path/to/private_key"
}
```

## EC2のインスタンスタイプの変更

以下のようなファイルを作成する。

tf-manifests/simple-flask/override.tf

```
module "common_resources" {
  instance_type = "t2.xlarge"
}
```

※参考
https://developer.hashicorp.com/terraform/language/files/override
