# 040. Network Connectivity Checker

マルチクラウド（AWS / Azure / GCP）向けに、インスタンスやマネージドサービスのネットワーク到達性を  
制御プレーン API から判定する Python スクリプトです。

## 概要

| プロバイダ | リソース種別 | `--resource-type` |
|-----------|------------|-----------------|
| AWS       | EC2        | `ec2`            |
| AWS       | RDS        | `rds`            |
| Azure     | Virtual Machine | `vm`        |
| GCP       | Compute Engine | `compute`    |
| GCP       | Cloud Run  | `cloudrun`       |
| GCP       | Cloud SQL  | `cloudsql`       |

---

## ファイル構成

```
040.network-connectivity-checker/
├── README.md
├── pytest.ini
├── requirements.txt
├── terraform.tf          ← Terraform プロバイダ設定
├── variables.tf          ← Terraform 変数定義
├── aws.tf                ← AWS リソース (VPC / Subnet / SG / EC2 / RDS)
├── azure.tf              ← Azure リソース (VNet / NSG / VM)
├── gcp.tf                ← GCP リソース (VPC / Firewall / VM / Cloud Run / LB)
├── outputs.tf            ← Terraform 出力値（結合テスト用リソース ID）
├── sample_output/
│   ├── aws_ec2_sample.json
│   ├── aws_rds_sample.json
│   ├── azure_vm_sample.json
│   ├── gcp_compute_sample.json
│   ├── gcp_cloudrun_sample.json
│   └── gcp_cloudsql_sample.json
├── scripts/
│   └── check_network_connectivity.py   ← メインスクリプト（単一ファイル）
└── tests/
    ├── conftest.py
    └── test_check_network_connectivity.py
```

---

## 必要権限

### AWS

| リソース | 必要な IAM アクション |
|---------|---------------------|
| EC2 | `ec2:DescribeInstances` `ec2:DescribeSecurityGroups` `ec2:DescribeRouteTables` `ec2:DescribeSubnets` `elasticloadbalancing:DescribeTargetGroups` `elasticloadbalancing:DescribeTargetHealth` `elasticloadbalancing:DescribeLoadBalancers` |
| RDS | `rds:DescribeDBInstances` `ec2:DescribeSecurityGroups` |

最小権限ポリシー例（AWS マネージドポリシー）:
- `AmazonEC2ReadOnlyAccess`
- `AmazonRDSReadOnlyAccess`

### Azure

以下のロールが必要です（リソース グループ スコープ以上）:

- `Reader`

追加で NetworkInterface / PublicIPAddress / NSG / RouteTable の参照が必要なため、  
`Network Contributor` または `Reader` + `Microsoft.Network/*/read` 権限を付与してください。

### GCP

以下の IAM ロールが必要です：

| リソース | 必要なロール |
|---------|-----------|
| Compute Engine | `roles/compute.viewer` |
| Cloud Run | `roles/run.viewer` + `roles/compute.viewer` |
| Cloud SQL | `roles/cloudsql.viewer` |

または `roles/viewer`（プロジェクト閲覧者）でも代替可能です。

---

## 認証手順

### AWS

```bash
# 方法1: AWS CLI プロファイルを使用
aws configure

# 方法2: 環境変数で設定
export AWS_ACCESS_KEY_ID=<your-key-id>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_DEFAULT_REGION=ap-northeast-1

# 方法3: IAM ロール（EC2 インスタンスプロファイル / ECS タスクロール）
# 特別な設定不要（自動的に認証情報が取得されます）
```

### Azure

```bash
# Azure CLI でログイン
az login

# またはサービスプリンシパルで認証
export AZURE_CLIENT_ID=<your-client-id>
export AZURE_CLIENT_SECRET=<your-client-secret>
export AZURE_TENANT_ID=<your-tenant-id>
```

### GCP

```bash
# gcloud でアプリケーションデフォルト認証を設定
gcloud auth application-default login

# またはサービスアカウントキーを使用
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

---

## インストール

```bash
cd 040.network-connectivity-checker
pip install -r requirements.txt
```

---

## 実行方法

### 共通オプション

```
usage: check_network_connectivity.py [-h]
  --provider {aws,azure,gcp}
  --resource-type {ec2,rds,vm,compute,cloudrun,cloudsql}
  --resource-id RESOURCE_ID
  [--region REGION]
  [--lb-backend-service LB_BACKEND_SERVICE]
  [--profile PROFILE]
  [--output OUTPUT]
```

| オプション | 説明 |
|-----------|------|
| `--provider` | クラウドプロバイダ (`aws` / `azure` / `gcp`) |
| `--resource-type` | リソース種別 |
| `--resource-id` | リソース識別子（種別ごとに異なる、後述） |
| `--region` | AWS リージョン（省略時は環境変数 `AWS_DEFAULT_REGION` を参照） |
| `--lb-backend-service` | GCP Cloud Run 判定時に、複数候補から絞り込む任意の Backend Service 名 |
| `--profile` | **AWS のみ** 使用する名前付きプロファイル（省略時はデフォルト認証チェーンを使用） |
| `--output` | JSON 出力先ファイルパス（省略時は標準出力） |

---

### AWS EC2

```bash
python scripts/check_network_connectivity.py \
  --provider aws \
  --resource-type ec2 \
  --resource-id i-0abc1234567890def \
  --region ap-northeast-1

# AWS プロファイルを指定する場合
python scripts/check_network_connectivity.py \
  --provider aws \
  --resource-type ec2 \
  --resource-id i-0abc1234567890def \
  --region ap-northeast-1 \
  --profile myprofile
```

**`--resource-id`**: EC2 インスタンス ID（例: `i-0abc1234567890def`）  
**`--profile`**: AWS CLI で設定した名前付きプロファイル名（省略可）

---

### AWS RDS

```bash
python scripts/check_network_connectivity.py \
  --provider aws \
  --resource-type rds \
  --resource-id mydbinstance \
  --region ap-northeast-1

# AWS プロファイルを指定する場合
python scripts/check_network_connectivity.py \
  --provider aws \
  --resource-type rds \
  --resource-id mydbinstance \
  --region ap-northeast-1 \
  --profile myprofile
```

**`--resource-id`**: DB インスタンス識別子（例: `mydbinstance`）  
**`--profile`**: AWS CLI で設定した名前付きプロファイル名（省略可）

---

### Azure Virtual Machine

```bash
python scripts/check_network_connectivity.py \
  --provider azure \
  --resource-type vm \
  --resource-id "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Compute/virtualMachines/<vm-name>"
```

**`--resource-id`**: Azure リソース ID（フルパス）

---

### GCP Compute Engine

```bash
python scripts/check_network_connectivity.py \
  --provider gcp \
  --resource-type compute \
  --resource-id "projects/<project-id>/zones/<zone>/instances/<instance-name>"
```

**`--resource-id`**: `projects/<project>/zones/<zone>/instances/<name>` 形式

---

### GCP Cloud Run

```bash
python scripts/check_network_connectivity.py \
  --provider gcp \
  --resource-type cloudrun \
  --resource-id "projects/<project-id>/locations/<region>/services/<service-name>"
```

必要時のみ（複数候補から絞り込みたい場合）:

```bash
python scripts/check_network_connectivity.py \
  --provider gcp \
  --resource-type cloudrun \
  --resource-id "projects/<project-id>/locations/<region>/services/<service-name>" \
  --lb-backend-service "<optional-backend-service-name>"
```

**`--resource-id`**: `projects/<project>/locations/<region>/services/<name>` 形式

Cloud Run 判定では、Cloud Run Service -> サーバレス NEG -> Backend Service -> URL Map / Proxy / Forwarding Rule を逆引きし、
ロードバランサ経由の到達可能性を設定から推定します。

---

### GCP Cloud SQL

```bash
python scripts/check_network_connectivity.py \
  --provider gcp \
  --resource-type cloudsql \
  --resource-id "projects/<project-id>/instances/<instance-name>"
```

**`--resource-id`**: `projects/<project>/instances/<name>` 形式

---

## 出力 JSON フォーマット

```json
{
  "provider": "aws | azure | gcp",
  "resource_type": "ec2 | rds | vm | compute | cloudrun | cloudsql",
  "resource_id": "<指定したリソース ID>",
  "internet_reachability": "reachable | not_reachable | unknown",
  "private_reachability": "reachable | not_reachable | unknown",
  "reasons": [
    "instance_state=running",
    "public_subnet=true",
    "public_ip_assigned=true",
    "sg_ingress_allows=0.0.0.0/0"
  ],
  "observed": {
    "instance_state": "running",
    "public_subnet": true,
    "private_ip": "10.0.1.10",
    "public_ip": "203.0.113.10",
    "public_ip_assigned": true,
    "security_groups": [
      {
        "group_id": "sg-0123456789abcdef0",
        "group_name": "web-sg",
        "ingress_rules": [
          {
            "cidr": "0.0.0.0/0",
            "protocol": "tcp",
            "from_port": 443,
            "to_port": 443
          }
        ],
        "egress_rules": [
          {
            "cidr": "0.0.0.0/0",
            "protocol": "-1",
            "from_port": null,
            "to_port": null
          }
        ]
      }
    ]
  }
}
```

サンプル出力は `sample_output/` ディレクトリを参照してください。

Azure VM の場合、`observed` には NSG 情報として以下が含まれます。

```json
{
  "power_state": "running",
  "private_ips": ["10.0.0.4"],
  "public_ips": ["1.2.3.4"],
  "subnet_ids": [
    "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Network/virtualNetworks/<vnet>/subnets/<subnet>"
  ],
  "has_udr": false,
  "nsg_rules": [
    {
      "nsg_name": "nic-nsg",
      "allow_rules": [
        {
          "name": "AllowHTTPS",
          "direction": "Inbound",
          "priority": 100,
          "protocol": "Tcp",
          "source_address_prefix": "0.0.0.0/0",
          "destination_address_prefix": "*",
          "destination_port_range": "443"
        }
      ]
    }
  ],
  "subnet_nsg_rules": [
    {
      "nsg_name": "subnet-nsg",
      "allow_rules": [
        {
          "name": "AllowHTTPS",
          "direction": "Inbound",
          "priority": 100,
          "protocol": "Tcp",
          "source_address_prefix": "0.0.0.0/0",
          "destination_address_prefix": "*",
          "destination_port_range": "443"
        }
      ]
    }
  ]
}
```

また `reasons` には、NSG の観測有無として以下が追加されます。

- `nsg_rules_present_nic=true|false`
- `nsg_rules_present_subnet=true|false`
- `nsg_rules_present=true|false`（上記どちらかが true なら true）

---

## 判定ロジック

### AWS EC2

| 観点 | `internet_reachability` | `private_reachability` |
|-----|------------------------|----------------------|
| `instance_state=running` | 必須 | 必須 |
| `public_subnet=true` | 必須 | 不要 |
| `public_ip_assigned=true` | 必須 | 不要 |
| `private_ip` あり | 不要 | 必須 |

### AWS RDS

| 観点 | `internet_reachability` | `private_reachability` |
|-----|------------------------|----------------------|
| `db_state=available` | 必須 | 必須 |
| `publicly_accessible=true` | 必須 | 不要 |
| `vpc_id` あり | 不要 | 必須 |

### Azure VM

| 観点 | `internet_reachability` | `private_reachability` |
|-----|------------------------|----------------------|
| `power_state=running` | 必須 | 必須 |
| Public IP あり | 必須 | 不要 |
| Private IP あり | 不要 | 必須 |
| NIC NSG / Subnet NSG（allow ルール観測） | 参考情報 | 参考情報 |

### GCP Compute Engine

| 観点 | `internet_reachability` | `private_reachability` |
|-----|------------------------|----------------------|
| `instance_state=RUNNING` | 必須 | 必須 |
| External IP あり | 必須 | 不要 |
| Private IP あり | 不要 | 必須 |
| Firewall ルール（network tags で絞り込み） | 参考情報 | 参考情報 |

### GCP Cloud Run

| 観点 | `internet_reachability` | `private_reachability` |
|-----|------------------------|----------------------|
| `ingress=all` または `external` | 必須 | 充足 |
| `ingress=internal` | 不可 | Internal LB (`INTERNAL_MANAGED`) が1つ以上必要 |
| `ingress=internal-and-cloud-load-balancing` | 不可 | LB逆引きで有効LBが1つ以上必要 |
| `roles/run.invoker` の principal 数 | 参考情報 | 0件なら `not_reachable` |
| NEG/Backend/URL Map/Proxy/Forwarding Rule 参照権限不足 | 参考情報 | `unknown` |

### GCP Cloud SQL

| 観点 | `internet_reachability` | `private_reachability` |
|-----|------------------------|----------------------|
| `db_state=RUNNABLE` | 必須 | 必須 |
| Public IP 有効 (`ipv4Enabled=true`) | 必須 | 不要 |
| Private IP 設定あり (`privateNetwork`) | 不要 | 必須 |

---

## テスト実行

```bash
cd 040.network-connectivity-checker
pip install -r requirements.txt
pytest
```

---

## 注意事項

- 本スクリプトは **読み取り専用 API のみ** を使用します（変更系 API は実行しません）
- 実疎通テスト（TCP/ICMP 等のアクティブプローブ）は行いません
- 制御プレーン API の設定状態に基づく判定のため、実際のパケット通信とは異なる場合があります
- egress 方向の到達性（Cloud NAT 経由など）は本スクリプトの対象外です

---

## 結合テスト

### 前提条件

#### 必要なツール

| ツール | バージョン | 用途 |
|--------|-----------|------|
| [Terraform](https://developer.hashicorp.com/terraform/downloads) | >= 1.5.0 | インフラリソース作成 |
| [AWS CLI](https://aws.amazon.com/cli/) | >= 2.0 | AWS 認証 |
| [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) | >= 2.0 | Azure 認証 |
| [gcloud CLI](https://cloud.google.com/sdk/docs/install) | >= 450.0 | GCP 認証 |
| Python | >= 3.9 | スクリプト実行 |

#### 各クラウドの認証情報・権限

**AWS**

以下の IAM ポリシーを持つユーザー / ロールの認証情報を設定してください。

- `AmazonEC2FullAccess`（または VPC / EC2 作成に必要な権限）
- `AmazonRDSFullAccess`（または RDS 作成に必要な権限）

*bash / zsh*

```bash
aws configure
# または
export AWS_ACCESS_KEY_ID=<your-key-id>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_DEFAULT_REGION=ap-northeast-1
```

*PowerShell*

```powershell
aws configure
# または
$env:AWS_ACCESS_KEY_ID     = "<your-key-id>"
$env:AWS_SECRET_ACCESS_KEY = "<your-secret-key>"
$env:AWS_DEFAULT_REGION    = "ap-northeast-1"
```

**Azure**

以下のロールをサブスクリプション / リソースグループスコープで付与してください。

- `Contributor`（リソース作成・削除に必要）

*bash / zsh*

```bash
az login
export TF_VAR_azure_subscription_id=$(az account show --query id -o tsv)
```

*PowerShell*

```powershell
az login
$env:TF_VAR_azure_subscription_id = $(az account show --query id -o tsv)
```

**GCP**

以下の IAM ロールをプロジェクトスコープで付与してください。

- `roles/compute.admin`
- `roles/run.admin`
- `roles/iam.serviceAccountUser`

*bash / zsh*

```bash
gcloud auth application-default login
export TF_VAR_gcp_project_id=<your-gcp-project-id>
```

*PowerShell*

```powershell
gcloud auth application-default login
$env:TF_VAR_gcp_project_id = "<your-gcp-project-id>"
```

---

### 作成されるリソース

| クラウド | リソース種別 | 名前 | 用途 |
|---------|------------|------|------|
| AWS | VPC | `ncc-test-vpc` | テスト用ネットワーク |
| AWS | Subnet (public) | `ncc-test-public-subnet` | EC2 用パブリックサブネット |
| AWS | Subnet (private) | `ncc-test-private-subnet` | RDS 用プライベートサブネット |
| AWS | Internet Gateway | `ncc-test-igw` | インターネット接続 |
| AWS | Security Group (EC2) | `ncc-test-ec2-sg` | HTTP/HTTPS/SSH 許可 |
| AWS | Security Group (RDS) | `ncc-test-rds-sg` | VPC 内 MySQL のみ許可 |
| AWS | EC2 Instance | `ncc-test-ec2` | internet_reachability=reachable 確認用 |
| AWS | RDS Instance | `ncc-test-rds` | internet_reachability=not_reachable 確認用 |
| Azure | Resource Group | `ncc-test-rg` | リソースグループ |
| Azure | VNet | `ncc-test-vnet` | テスト用ネットワーク |
| Azure | NSG | `ncc-test-nsg` | HTTP/HTTPS/SSH 許可 + 8080 拒否ルール |
| Azure | VM | `ncc-test-vm` | internet_reachability=reachable 確認用 |
| GCP | VPC | `ncc-test-vpc` | テスト用ネットワーク |
| GCP | Firewall (allow) | `ncc-test-allow-http-https-ssh` | HTTP/HTTPS/SSH 許可 |
| GCP | Firewall (deny) | `ncc-test-deny-custom-port` | 8080 拒否ルール |
| GCP | VM Instance | `ncc-test-vm` | internet_reachability=reachable 確認用 |
| GCP | Cloud Run Service | `ncc-test-cloudrun` | internet_reachability=reachable 確認用 |
| GCP | Serverless NEG | `ncc-test-cloudrun-neg` | Cloud Run への LB バックエンド |
| GCP | Backend Service | `ncc-test-cloudrun-be` | Cloud Run 逆引き判定用 |
| GCP | URL Map / HTTP Proxy | `ncc-test-cloudrun-um` / `ncc-test-cloudrun-http-proxy` | HTTP LB 構成 |
| GCP | Global Forwarding Rule / IP | `ncc-test-cloudrun-http-fr` | LB 公開エンドポイント |

---

### 結合テスト手順

#### 1. リソース作成

> アクセス制御仕様: HTTP/HTTPS/SSH の許可元は Terraform 実行元のグローバル IP のみ（/32）です。  
> Cloud Run は `cloudrun_invoker_principal` で指定した principal のみ呼び出し可能です。  
> 実行環境がプロキシ/NAT 配下の場合、許可対象はその送信元グローバル IP になります。

*bash / zsh*

```bash
cd 040.network-connectivity-checker

# 変数ファイルを作成（機密情報はファイルまたは環境変数で渡す）
cat > terraform.tfvars <<'EOF'
aws_region              = "ap-northeast-1"
azure_location          = "japaneast"
gcp_region              = "asia-northeast1"
gcp_zone                = "asia-northeast1-a"
aws_rds_password        = "YourSecurePassword1!"
azure_vm_admin_password = "YourSecurePassword1!"
cloudrun_invoker_principal = "user:you@example.com"
EOF

# Terraform 初期化
terraform init

# 実行計画確認
terraform plan

# リソース作成（約 10〜15 分）
terraform apply
```

*PowerShell*

```powershell
Set-Location 040.network-connectivity-checker

# 変数ファイルを作成（機密情報はファイルまたは環境変数で渡す）
@"
aws_region              = "ap-northeast-1"
azure_location          = "japaneast"
gcp_region              = "asia-northeast1"
gcp_zone                = "asia-northeast1-a"
aws_rds_password        = "YourSecurePassword1!"
azure_vm_admin_password = "YourSecurePassword1!"
cloudrun_invoker_principal = "user:you@example.com"
"@ | Set-Content terraform.tfvars -Encoding UTF8

# Terraform 初期化
terraform init

# 実行計画確認
terraform plan

# リソース作成（約 10〜15 分）
terraform apply
```

> **注意**: `terraform.tfvars` はルートの `.gitignore` により自動的に Git の追跡対象外になっています。  
> パスワードを環境変数で渡す場合:  
> - bash: `export TF_VAR_aws_rds_password=<password>`  
> - PowerShell: `$env:TF_VAR_aws_rds_password = "<password>"`

#### 2. リソース ID の取得

*bash / zsh*

```bash
# すべての出力値を表示
terraform output

# 適用された許可 CIDR の確認
terraform output -raw effective_allowed_cidr

# 個別に取得
EC2_ID=$(terraform output -raw aws_ec2_instance_id)
RDS_ID=$(terraform output -raw aws_rds_identifier)
AZURE_VM_ID=$(terraform output -raw azure_vm_resource_id)
GCP_VM_ID=$(terraform output -raw gcp_vm_resource_id)
GCP_CLOUDRUN_ID=$(terraform output -raw gcp_cloudrun_resource_id)
GCP_CLOUDRUN_LB_BACKEND=$(terraform output -raw gcp_cloudrun_lb_backend_service)
GCP_CLOUDRUN_LB_URL=$(terraform output -raw gcp_cloudrun_lb_url)
GCP_CLOUDSQL_ID=$(terraform output -raw gcp_cloudsql_resource_id)
```

*PowerShell*

```powershell
# すべての出力値を表示
terraform output

# 適用された許可 CIDR の確認
terraform output -raw effective_allowed_cidr

# 個別に取得
$EC2_ID         = terraform output -raw aws_ec2_instance_id
$RDS_ID         = terraform output -raw aws_rds_identifier
$AZURE_VM_ID    = terraform output -raw azure_vm_resource_id
$GCP_VM_ID      = terraform output -raw gcp_vm_resource_id
$GCP_CLOUDRUN_ID = terraform output -raw gcp_cloudrun_resource_id
$GCP_CLOUDRUN_LB_BACKEND = terraform output -raw gcp_cloudrun_lb_backend_service
$GCP_CLOUDRUN_LB_URL = terraform output -raw gcp_cloudrun_lb_url
$GCP_CLOUDSQL_ID = terraform output -raw gcp_cloudsql_resource_id
```

#### 3. 結合テスト実行

*bash / zsh*

```bash
cd 040.network-connectivity-checker
pip install -r requirements.txt

# AWS EC2（internet_reachability=reachable を確認）
python scripts/check_network_connectivity.py \
  --provider aws \
  --resource-type ec2 \
  --resource-id "${EC2_ID}" \
  --region ap-northeast-1

# AWS RDS（internet_reachability=not_reachable を確認）
python scripts/check_network_connectivity.py \
  --provider aws \
  --resource-type rds \
  --resource-id "${RDS_ID}" \
  --region ap-northeast-1

# Azure VM（internet_reachability=reachable を確認）
python scripts/check_network_connectivity.py \
  --provider azure \
  --resource-type vm \
  --resource-id "${AZURE_VM_ID}"

# GCP Compute Engine（internet_reachability=reachable を確認）
python scripts/check_network_connectivity.py \
  --provider gcp \
  --resource-type compute \
  --resource-id "${GCP_VM_ID}"

# GCP Cloud Run（internet_reachability=reachable を確認）
python scripts/check_network_connectivity.py \
  --provider gcp \
  --resource-type cloudrun \
  --resource-id "${GCP_CLOUDRUN_ID}"

# 必要時のみ: Backend Service 名で候補を絞り込む
python scripts/check_network_connectivity.py \
  --provider gcp \
  --resource-type cloudrun \
  --resource-id "${GCP_CLOUDRUN_ID}" \
  --lb-backend-service "${GCP_CLOUDRUN_LB_BACKEND}"
```

*PowerShell*

```powershell
Set-Location 040.network-connectivity-checker
pip install -r requirements.txt

# AWS EC2（internet_reachability=reachable を確認）
python scripts/check_network_connectivity.py `
  --provider aws `
  --resource-type ec2 `
  --resource-id $EC2_ID `
  --region ap-northeast-1

# AWS RDS（internet_reachability=not_reachable を確認）
python scripts/check_network_connectivity.py `
  --provider aws `
  --resource-type rds `
  --resource-id $RDS_ID `
  --region ap-northeast-1

# Azure VM（internet_reachability=reachable を確認）
python scripts/check_network_connectivity.py `
  --provider azure `
  --resource-type vm `
  --resource-id $AZURE_VM_ID

# GCP Compute Engine（internet_reachability=reachable を確認）
python scripts/check_network_connectivity.py `
  --provider gcp `
  --resource-type compute `
  --resource-id $GCP_VM_ID

# GCP Cloud Run（internet_reachability=reachable を確認）
python scripts/check_network_connectivity.py `
  --provider gcp `
  --resource-type cloudrun `
  --resource-id $GCP_CLOUDRUN_ID

# 必要時のみ: Backend Service 名で候補を絞り込む
python scripts/check_network_connectivity.py `
  --provider gcp `
  --resource-type cloudrun `
  --resource-id $GCP_CLOUDRUN_ID `
  --lb-backend-service $GCP_CLOUDRUN_LB_BACKEND
```

#### 期待する結合テスト結果

| リソース | `internet_reachability` | `private_reachability` |
|---------|------------------------|----------------------|
| AWS EC2 | `reachable` | `reachable` |
| AWS RDS | `not_reachable` | `reachable` |
| Azure VM | `reachable` | `reachable` |
| GCP VM | `reachable` | `reachable` |
| GCP Cloud Run | `reachable` | `reachable` |

#### 4. リソース削除

**テスト完了後は必ずリソースを削除してコストを抑えてください。**

*bash / zsh*

```bash
cd 040.network-connectivity-checker
terraform destroy
```

*PowerShell*

```powershell
Set-Location 040.network-connectivity-checker
terraform destroy
```

---

### コスト見積もり

> 以下は **東京リージョン（ap-northeast-1 / japaneast / asia-northeast1）** での概算です。  
> 実際の料金は利用量・プラン・為替により異なります。

| クラウド | リソース | 種別 | 概算コスト（時間） | 概算コスト（月） |
|---------|---------|------|---------------|--------------|
| AWS | EC2 (t3.micro) | コンピュート | $0.013 | ~$9.5 |
| AWS | RDS MySQL (db.t3.micro) | データベース | $0.026 | ~$18.9 |
| AWS | VPC / Subnet / SG | ネットワーク | $0.00 | $0.00 |
| Azure | VM (Standard_B1s) | コンピュート | $0.012 | ~$8.8 |
| Azure | VNet / NSG | ネットワーク | $0.00 | $0.00 |
| Azure | Public IP (Static Standard) | ネットワーク | ~$0.005 | ~$3.6 |
| GCP | VM (e2-micro) | コンピュート | $0.008 | ~$5.8 |
| GCP | Cloud Run | サーバーレス | 従量課金（リクエスト時のみ） | ~$0〜 |
| GCP | VPC / Firewall | ネットワーク | $0.00 | $0.00 |
| **合計** | | | | **~$46.6 / 月** |

> **推奨**: 結合テストは作成・実行・削除を 1〜2 時間以内に完了させることで、コストを **$2 未満** に抑えられます。

---

### 注意事項（結合テスト）

- `terraform.tfvars` にパスワードを記載する場合は `.gitignore` に追加し、リポジトリにコミットしないこと
- テスト完了後は `terraform destroy` で必ずリソースを削除すること
- RDS の起動には約 5〜10 分かかります。`terraform apply` 完了後すぐにテストを実行してください
- GCP Cloud Run の初回デプロイには約 2〜3 分かかる場合があります
