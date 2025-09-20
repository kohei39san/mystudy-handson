# OCI Container Instances Redmine デプロイメント

このTerraformコードは、Oracle Cloud Infrastructure (OCI) 上にRedmineアプリケーションをデプロイするためのものです。Container InstancesとMySQL HeatWaveを使用して、スケーラブルで管理しやすいRedmine環境を構築します。

## アーキテクチャ概要

### 構成要素

1. **OCI Container Instances**
   - イメージ: `bitnami/redmine:6.0.6`
   - シェイプ: Ampere A1 Flex (1 OCPU, 4GB メモリ)
   - プライベートサブネット内に配置

2. **Oracle MySQL HeatWave**
   - ノード数: 1
   - シェイプ: MySQL.Free
   - 専用サブネット内に配置

3. **OCI Network Load Balancer**
   - パブリックサブネット内に配置
   - 指定されたCIDRからのアクセスのみ許可
   - HTTP/HTTPS トラフィックを処理

4. **ネットワーク構成**
   - VCN: 10.0.0.0/16
   - パブリックサブネット: 10.0.1.0/24 (Load Balancer用)
   - プライベートサブネット: 10.0.2.0/24 (Container Instance用)
   - MySQLサブネット: 10.0.3.0/24 (MySQL HeatWave用)

### セキュリティ

- Container Instancesはプライベートサブネット内に配置
- MySQL HeatWaveは専用サブネット内に配置
- Network Load Balancerは指定されたCIDRからのアクセスのみ許可
- セキュリティリストとNSGによる適切なトラフィック制御

## 前提条件

1. **OCI CLI の設定**
   ```bash
   oci setup config
   ```

2. **Terraform のインストール**
   - Terraform 1.0以上が必要

3. **必要な権限**
   - Compute管理権限
   - Networking管理権限
   - MySQL管理権限
   - Container Instance管理権限
   - Load Balancer管理権限

## デプロイメント手順

### 1. 設定ファイルの準備

`terraform.tfvars.example`をコピーして`terraform.tfvars`を作成し、適切な値を設定してください：

```bash
cp terraform.tfvars.example terraform.tfvars
```

### 2. 必須変数の設定

`terraform.tfvars`ファイルで以下の変数を設定してください：

```hcl
# OCI設定
region         = "ap-osaka-1"
compartment_id = "your-compartment-ocid"

# アクセス制御
allowed_cidr = "your-allowed-ip-range/24"

# MySQL設定
mysql_admin_password = "secure-mysql-password"

# Redmine設定
redmine_db_password    = "secure-redmine-db-password"
redmine_admin_username = "admin"
redmine_admin_password = "secure-redmine-admin-password"
redmine_admin_email    = "admin@yourcompany.com"
```

### 3. Terraformの実行

```bash
# 初期化
terraform init

# プランの確認
terraform plan

# デプロイメント実行
terraform apply
```

### 4. デプロイメント完了後

デプロイメントが完了すると、以下の情報が出力されます：

- `load_balancer_ip`: Load BalancerのパブリックIPアドレス
- `redmine_url`: RedmineアプリケーションのURL

## アクセス方法

1. **Redmineへのアクセス**
   - ブラウザで `http://<load_balancer_ip>` にアクセス
   - 初期ログイン情報:
     - ユーザー名: `terraform.tfvars`で設定した`redmine_admin_username`
     - パスワード: `terraform.tfvars`で設定した`redmine_admin_password`

2. **データベースの初期化**
   - Redmineの初回起動時に自動的にデータベースが初期化されます
   - 必要に応じて追加の設定を行ってください

## 運用・保守

### モニタリング

1. **Container Instancesの監視**
   - OCI Consoleでコンテナの状態を確認
   - ログの確認とトラブルシューティング

2. **MySQL HeatWaveの監視**
   - データベースのパフォーマンス監視
   - バックアップの状態確認

3. **Load Balancerの監視**
   - ヘルスチェックの状態確認
   - トラフィック分散の監視

### バックアップ

- MySQL HeatWaveは自動バックアップが有効（7日間保持）
- Redmineのファイルデータは必要に応じて別途バックアップを検討

### スケーリング

- Container Instancesのリソース（OCPU/メモリ）は必要に応じて調整可能
- MySQL HeatWaveのストレージサイズも拡張可能

## トラブルシューティング

### よくある問題

1. **Container Instanceが起動しない**
   - セキュリティリストの設定を確認
   - MySQL HeatWaveへの接続設定を確認

2. **Load Balancerからアクセスできない**
   - `allowed_cidr`の設定を確認
   - セキュリティリストのルールを確認

3. **データベース接続エラー**
   - MySQL HeatWaveの状態を確認
   - データベース認証情報を確認

### ログの確認方法

```bash
# Container Instanceのログ確認
oci container-instances container-instance get-container-logs \
  --container-instance-id <container-instance-id> \
  --container-name redmine
```

## セキュリティ考慮事項

1. **パスワード管理**
   - 強力なパスワードを使用
   - 定期的なパスワード変更を実施

2. **ネットワークセキュリティ**
   - `allowed_cidr`を適切に制限
   - 不要なポートは開放しない

3. **アクセス制御**
   - OCI IAMポリシーによる適切なアクセス制御
   - 最小権限の原則を適用

## コスト最適化

1. **MySQL.Freeシェイプの使用**
   - 開発・テスト環境に適した無料枠を活用

2. **Ampere A1 Flexの使用**
   - コストパフォーマンスに優れたARMベースのプロセッサ

3. **リソースの適切なサイジング**
   - 使用量に応じたリソース調整

## リソースの削除

環境を削除する場合は以下のコマンドを実行してください：

```bash
terraform destroy
```

**注意**: この操作により、すべてのリソースとデータが削除されます。重要なデータは事前にバックアップを取得してください。

## サポート・問い合わせ

- OCI公式ドキュメント: https://docs.oracle.com/ja-jp/iaas/
- Redmine公式ドキュメント: https://www.redmine.org/guide
- Bitnami Redmineドキュメント: https://docs.bitnami.com/oci/apps/redmine/

## ライセンス

このTerraformコードはMITライセンスの下で提供されています。