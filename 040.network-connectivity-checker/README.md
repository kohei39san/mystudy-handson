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
| EC2 | `ec2:DescribeInstances` `ec2:DescribeSecurityGroups` `ec2:DescribeRouteTables` `ec2:DescribeSubnets` |
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
| Cloud Run | `roles/run.viewer` |
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
  [--output OUTPUT]
```

| オプション | 説明 |
|-----------|------|
| `--provider` | クラウドプロバイダ (`aws` / `azure` / `gcp`) |
| `--resource-type` | リソース種別 |
| `--resource-id` | リソース識別子（種別ごとに異なる、後述） |
| `--region` | AWS リージョン（省略時は環境変数 `AWS_DEFAULT_REGION` を参照） |
| `--output` | JSON 出力先ファイルパス（省略時は標準出力） |

---

### AWS EC2

```bash
python scripts/check_network_connectivity.py \
  --provider aws \
  --resource-type ec2 \
  --resource-id i-0abc1234567890def \
  --region ap-northeast-1
```

**`--resource-id`**: EC2 インスタンス ID（例: `i-0abc1234567890def`）

---

### AWS RDS

```bash
python scripts/check_network_connectivity.py \
  --provider aws \
  --resource-type rds \
  --resource-id mydbinstance \
  --region ap-northeast-1
```

**`--resource-id`**: DB インスタンス識別子（例: `mydbinstance`）

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

**`--resource-id`**: `projects/<project>/locations/<region>/services/<name>` 形式

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
    "public_ip_assigned": true
  }
}
```

サンプル出力は `sample_output/` ディレクトリを参照してください。

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
| `ingress=internal` または `internal-and-cloud-load-balancing` | 不可 | 必須 |

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
