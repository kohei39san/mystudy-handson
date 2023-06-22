# 概要

勉強で使った基盤はTerraformで作りました。このディレクトリではTerraformで使用したファイルを配置し、使い方について記載します。

# フォルダ構成

* tf-manifests/common: 各基盤で共通の要素を定義しています。
* tf-manifests/k0s: シングルノードでk0sを構築する設定を定義しています。（参考：https://k0sproject.io/）
* tf-manifests/scripts: DockerやKubernetesをインストールするためのスクリプトが入っています。
