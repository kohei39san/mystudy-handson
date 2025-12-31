# kubectl proxy Docker Compose

Kubernetes APIサーバーへのローカルプロキシを作成するDocker Composeファイルです。

## 概要

`kubectl proxy`をDockerコンテナで実行し、ローカルマシンからKubernetes APIにアクセスできるプロキシサーバーを提供します。

## 前提条件

- Docker および Docker Compose がインストールされていること
- Docker DesktopにてkindによるKubernetesクラスターのセットアップが完了していること

## 使用方法

### 1. 環境変数の設定（オプション）

環境変数ファイル（.env）を使用してkubectl proxyの設定をカスタマイズできます。

**.envファイルの作成:**
```bash
# .env.exampleをコピーして.envファイルを作成
cp .env.example .env
```

**.envファイルの設定例:**
```env
# プロキシサーバーの設定
PROXY_ADDRESS=0.0.0.0
PROXY_PORT=8001
ACCEPT_HOSTS=.*
LOG_LEVEL=2

# Kubernetesクラスター接続設定
K8S_ORIGINAL_SERVER=https://127.0.0.1:55420
K8S_TARGET_SERVER=https://host.docker.internal:55420
INSECURE_SKIP_TLS=true
```

**設定可能な環境変数:**
- `PROXY_ADDRESS`: プロキシのバインドアドレス（デフォルト: 0.0.0.0）
- `PROXY_PORT`: プロキシのポート番号（デフォルト: 8001）
- `ACCEPT_HOSTS`: 接続を許可するホストパターン（デフォルト: .*）
- `LOG_LEVEL`: kubectlのログレベル（デフォルト: 2）
- `K8S_ORIGINAL_SERVER`: 置き換え元のKubernetesサーバーURL
- `K8S_TARGET_SERVER`: 置き換え先のKubernetesサーバーURL
- `INSECURE_SKIP_TLS`: TLS証明書検証をスキップ（デフォルト: true）

### 2. Docker Composeでサービスを開始

```bash
docker-compose up -d
```

### 3. プロキシの動作確認（kubectl-proxyコンテナ内での実行）

```bash
# APIサーバーの情報を取得
curl http://localhost:8001/api/v1

# Namespace一覧を取得
curl http://localhost:8001/api/v1/namespaces

# Pod一覧を取得（default namespace）
curl http://localhost:8001/api/v1/namespaces/default/pods
```

### 4. サービスの停止

```bash
docker-compose down
```

## CRD（Custom Resource Definition）テスト

kubectl proxy経由でCRDのAPIアクセスをテストできます：

### CRD管理コマンド

**kubectl-proxyコンテナ内で直接実行:**
```bash
# コンテナに接続
docker compose exec kubectl-proxy sh

# 1. テンプレートからYAMLファイルを生成（必須）
./scripts/manage-crd.sh generate

# 2. CRD操作（コンテナ内）
./scripts/manage-crd.sh install        # CRDをインストール
./scripts/manage-crd.sh create-samples # サンプルリソースを作成
./scripts/manage-crd.sh test-api       # APIテスト
./scripts/manage-crd.sh list           # リソース一覧確認
./scripts/manage-crd.sh delete-samples # サンプルリソース削除
./scripts/manage-crd.sh uninstall      # CRDをアンインストール
./scripts/manage-crd.sh clean          # 生成ファイル削除

# コンテナから退出
exit
```

**または、ホストから直接実行:**
```bash
# 1. テンプレートからYAMLファイルを生成
docker compose exec kubectl-proxy ./scripts/manage-crd.sh generate

# 2. CRDをインストール
docker compose exec kubectl-proxy ./scripts/manage-crd.sh install

# 3. サンプルリソースを作成
docker compose exec kubectl-proxy ./scripts/manage-crd.sh create-samples

# 4. APIテスト
docker compose exec kubectl-proxy ./scripts/manage-crd.sh test-api
```

### 作成されるCRDの概要

- **API Group**: `example.com`
- **Kind**: `Website` (設定で変更可能)
- **機能**: Webサイト設定の管理
- **フィールド**: URL, レプリカ数, ポート, SSL設定, 環境設定など
- **テンプレートファイル**: `src/crd-template.yaml`, `src/resource-template.yaml`
- **設定ファイル**: `scripts/crd-config.sh`
- **生成されるファイル**: `src/*-generated.yaml`

**注意**: `generate`コマンドでテンプレートからYAMLファイルを生成することが必須です。

## カスタマイズ例

### 異なるポートで実行

**.envファイル:**
```env
PROXY_PORT=9000
```

```bash
# ポート9000でプロキシを起動
docker-compose up -d

# アクセステスト
curl http://localhost:9000/api/v1
```

### セキュリティを強化

**.envファイル:**
```env
PROXY_ADDRESS=127.0.0.1
ACCEPT_HOSTS=^localhost$,^127\\.0\\.0\\.1$
INSECURE_SKIP_TLS=false
```

### デバッグモード

**.envファイル:**
```env
LOG_LEVEL=5
```

## 設定項目

- **ポート**: `8001` (デフォルトのkubectl proxyポート)
- **アドレス**: `0.0.0.0` (すべてのインターフェースでリッスン)
- **Kubeconfig**: `${HOME}/.kube/config` をコンテナ内にマウント

## 注意事項

- **Windows + Docker Desktop環境**: このプロジェクトは Windows環境の Docker Desktop Kubernetes 用に最適化されています
- **Kubeconfigパス**: `C:\Users\user\.kube\config` を使用するように設定済みです
- **Docker Desktop Kubernetes**: ローカルのDocker Desktop Kubernetesクラスター（`https://127.0.0.1:55420`）に接続します
- **セキュリティ**: このプロキシは認証なしでKubernetes APIへのアクセスを提供します。本番環境では適切な認証・認可機能を実装してください
- **ネットワーク**: `--accept-hosts=.*` により外部からのアクセスを許可しています。必要に応じて制限してください

## curl API操作ガイド

kubectl proxyを通してcurlでKubernetes APIを直接操作するためのスクリプトが含まれています。

### 前提条件

- kubectl proxyが起動していること（`docker compose up -d`で起動）
- jqコマンドが利用可能であること（bitnami/kubectlイメージに含まれています）

### 基本的な使用例

#### 1. API情報の確認
```bash
# コンテナ内で実行
./scripts/curl-api.sh api-info
```

#### 2. 名前空間操作
```bash
# 名前空間一覧
./scripts/curl-api.sh list-namespaces

# 名前空間作成（生成ファイル使用）
./scripts/curl-api.sh create-namespace

# 名前空間削除
./scripts/curl-api.sh delete-namespace

# 特定の名前空間詳細
./scripts/curl-api.sh get-namespace
```

#### 3. CRD操作
```bash
# CRD一覧表示
./scripts/curl-api.sh list-crds

# Website CRDの詳細
./scripts/curl-api.sh get-crd
```

#### 4. カスタムリソース操作
```bash
# Websiteリソース一覧
./scripts/curl-api.sh list-websites

# 新しいWebsiteリソース作成（生成ファイル使用）
./scripts/curl-api.sh create-website

# 特定のWebsiteリソース取得
./scripts/curl-api.sh get-website my-test-site

# リソースの更新（patch）
./scripts/curl-api.sh patch-website my-test-site

# リソースの削除
./scripts/curl-api.sh delete-website my-test-site
```

#### 5. 監視操作
```bash
# リソース変更の監視（リアルタイム）
./scripts/curl-api.sh watch-websites
```

### 完全なワークフロー例

```bash
# 1. コンテナに接続
docker exec -it kubectl-proxy sh

# 2. 全YAMLファイル生成
./scripts/manage-crd.sh generate

# 3. 名前空間作成
./scripts/manage-crd.sh create-namespace

# または、curlを使用して名前空間作成
./scripts/curl-api.sh create-namespace

# 4. CRDインストール
./scripts/manage-crd.sh install

# 5. curlでAPI確認
./scripts/curl-api.sh api-info
./scripts/curl-api.sh get-crd

# 6. curlでリソース作成・管理
./scripts/curl-api.sh create-website test-site
./scripts/curl-api.sh list-websites
./scripts/curl-api.sh patch-website test-site
./scripts/curl-api.sh get-website test-site

# 7. 監視（別ターミナルで）
./scripts/curl-api.sh watch-websites
```

### APIエンドポイント解説

| 操作 | HTTP Method | エンドポイント |
|------|-------------|----------------|
| API情報 | GET | `/version` |
| 名前空間一覧 | GET | `/api/v1/namespaces` |
| 名前空間作成 | POST | `/api/v1/namespaces` |
| 名前空間削除 | DELETE | `/api/v1/namespaces/{name}` |
| CRD一覧 | GET | `/apis/apiextensions.k8s.io/v1/customresourcedefinitions` |
| Website一覧 | GET | `/apis/example.com/v1/namespaces/{ns}/websites` |
| Website作成 | POST | `/apis/example.com/v1/namespaces/{ns}/websites` |
| Website取得 | GET | `/apis/example.com/v1/namespaces/{ns}/websites/{name}` |
| Website更新 | PATCH | `/apis/example.com/v1/namespaces/{ns}/websites/{name}` |
| Website削除 | DELETE | `/apis/example.com/v1/namespaces/{ns}/websites/{name}` |