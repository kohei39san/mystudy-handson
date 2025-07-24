# Amazon EKS クラスター構成

## 概要

このTerraform構成は、プライベートなAmazon EKSクラスターと、そのクラスターを管理するためのEC2インスタンスを作成します。クラスターはプライベートエンドポイントのみを持ち、EC2 Instance Connect Endpointを介してアクセスします。

## リソース構成

### ネットワークリソース
- **VPC**:
  - CIDRブロック: 10.0.0.0/16
- **サブネット**:
  - 2つのサブネット（異なるアベイラビリティゾーンに配置）
  - CIDRブロック: 10.0.0.0/24, 10.0.1.0/24
- **インターネットゲートウェイ**
- **ルートテーブル**:
  - インターネットゲートウェイへのルート
- **セキュリティグループ**:
  - EKSクラスター用: ポート443のみ許可

### EKSリソース
- **EKSクラスター**:
  - バージョン: 1.27
  - プライベートエンドポイントのみ有効
  - パブリックエンドポイント無効
- **EKSノードグループ**:
  - インスタンスタイプ: t2.micro
  - 最小サイズ: 0
  - 最大サイズ: 1
  - 希望サイズ: 0

### 管理リソース
- **EC2インスタンス**:
  - Amazon Linux 2 AMI
  - インスタンスタイプ: t2.micro
  - kubectl インストール済み
- **EC2 Instance Connect Endpoint**:
  - プライベートサブネットのEC2インスタンスへの接続用

### IAMリソース
- **EKSクラスターロール**:
  - AmazonEKSClusterPolicy
  - AmazonEKSServicePolicy
- **EKSノードロール**:
  - AmazonEKSWorkerNodePolicy
  - AmazonEKS_CNI_Policy
  - AmazonEC2ContainerRegistryReadOnly
- **kubectl管理インスタンスロール**:
  - EKSクラスター管理権限

## 変数

- **cluster_name**: EKSクラスターの名前（デフォルト: "eks-study"）
- **cluster_version**: EKSクラスターのバージョン（デフォルト: "1.27"）
- **node_instance_types**: ノードグループのインスタンスタイプ（デフォルト: ["t2.micro"]）
- **node_desired_size**: ノードグループの希望サイズ（デフォルト: 0）
- **node_max_size**: ノードグループの最大サイズ（デフォルト: 1）
- **node_min_size**: ノードグループの最小サイズ（デフォルト: 0）
- **vpc_cidr_block**: VPCのCIDRブロック（デフォルト: "10.0.0.0/16"）
- **num_subnets**: 作成するサブネットの数（デフォルト: 2）

## 使用方法

メインのREADME.mdに記載されている手順に従って、この構成をデプロイしてください。

## 注意事項

- このEKSクラスターはプライベートエンドポイントのみを持ち、パブリックアクセスはできません。
- クラスターへのアクセスには、EC2 Instance Connect Endpointを介して管理インスタンスに接続する必要があります。
- 本番環境での使用前に、セキュリティ設定とリソースサイズを見直してください。