# kubectl proxy Docker Compose

Kubernetes APIサーバーへのローカルプロキシを作成するDocker Composeファイルです。

![アーキテクチャ図](src/architecture.svg)

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

### 2. Dockerイメージのビルド

カスタムDockerfileを使用しているため、初回起動前またはDockerfile変更後はビルドが必要です：

```bash
# すべてのサービスをビルド
docker compose build

# 特定のサービスのみビルド
docker compose build kubectl-proxy
docker compose build ansible

# キャッシュを使わずにビルド（クリーンビルド）
docker compose build --no-cache
```

**カスタムイメージに含まれるもの：**
- **kubectl-proxy**: `socat`（HTTPS対応用）
- **ansible**: `curl`、`jmespath`（Ansible Playbookで使用）

### 3. Docker Composeでサービスを開始

```bash
# 基本的な起動（HTTPのみ）
docker compose up -d

# HTTPSを有効化して起動（統合モード）
ENABLE_HTTPS=true docker compose up -d

# または、.envファイルでENABLE_HTTPS=trueを設定してから起動
docker compose up -d
```

### 4. プロキシの動作確認（kubectl-proxyコンテナ内での実行）

```bash
# HTTPで接続確認
curl http://localhost:8001/api/v1

# HTTPS有効時の接続確認
curl -k https://localhost:8443/api/v1

# Namespace一覧を取得
curl http://localhost:8001/api/v1/namespaces

# Pod一覧を取得（default namespace）
curl http://localhost:8001/api/v1/namespaces/default/pods
```

### 5. サービスの停止

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

## Ansible操作ガイド

kubectl proxyを通してAnsibleでカスタムリソースを自動的に作成・管理できます。

### 前提条件

- Dockerイメージがビルド済みであること（`docker compose build`）
- kubectl proxyが起動していること（`docker compose up -d`で起動）
- CRDがインストールされていること（`docker exec kubectl-proxy ./scripts/manage-crd.sh generate && docker exec kubectl-proxy kubectl apply -f /src/crd-website-generated.yaml`）
- Ansibleコンテナが起動していること

### Ansibleサービスの起動

```bash
# 基本的な起動（HTTP接続）
docker compose up -d

# HTTPSを有効化して起動
docker compose --profile https up -d
```

### Ansibleプレイブック実行

2種類のPlaybookが利用可能です：
- **uriベース**: `ansible.builtin.uri`モジュールを使用（標準的なアプローチ）
- **curlベース**: `curl`コマンドを使用（より柔軟な制御が可能）

#### 1. カスタムリソース（Website）の作成

**uriベースのPlaybook:**
```bash
# Ansibleコンテナ内でプレイブックを実行
docker compose exec ansible ansible-playbook create-custom-resources.yml

# 環境変数で設定をカスタマイズして実行
docker compose exec -e RESOURCE_NAME=my-custom-site ansible ansible-playbook create-custom-resources.yml
```

**curlベースのPlaybook:**
```bash
# curlを使用したPlaybook実行
docker compose exec ansible ansible-playbook create-custom-resources-curl.yml

# カスタマイズして実行
docker compose exec -e RESOURCE_NAME=my-custom-site ansible ansible-playbook create-custom-resources-curl.yml
```

このプレイブックは以下の操作を実行します：
1. kubectl-proxyの接続確認
2. 名前空間の存在確認と作成（必要な場合）
3. CRDの存在確認
4. カスタムリソース（Website）の作成
5. 作成したリソースの詳細表示
6. 名前空間内の全リソース一覧表示

#### 2. カスタムリソースの削除

**uriベースのPlaybook:**
```bash
# リソースを削除
docker compose exec ansible ansible-playbook delete-custom-resources.yml

# 特定のリソースを削除
docker compose exec -e RESOURCE_NAME=my-custom-site ansible ansible-playbook delete-custom-resources.yml
```

**curlベースのPlaybook:**
```bash
# curlを使用した削除
docker compose exec ansible ansible-playbook delete-custom-resources-curl.yml

# 特定のリソースを削除
docker compose exec -e RESOURCE_NAME=my-custom-site ansible ansible-playbook delete-custom-resources-curl.yml
```

#### PlaybookとHTTPS接続

両方のPlaybook（uriベース、curlベース）は`ENABLE_HTTPS`環境変数に基づいて自動的にHTTP/HTTPSを切り替えます：

```bash
# HTTPで実行（デフォルト）
docker compose exec ansible ansible-playbook create-custom-resources.yml

# HTTPSで実行（ENABLE_HTTPS=trueの場合、自動的にhttps://kubectl-proxy:8443に接続）
docker compose exec ansible ansible-playbook create-custom-resources-curl.yml
```

#### 3. カスタマイズ可能な環境変数

Ansibleプレイブックでは以下の環境変数をカスタマイズできます：

```bash
# プロキシ接続設定
PROXY_PROTOCOL=http          # HTTPまたはHTTPS
PROXY_PORT=8001              # プロキシのポート番号

# CRD設定
CRD_GROUP=example.com        # CRDのAPIグループ
CRD_VERSION=v1               # CRDのバージョン
CRD_PLURAL=websites          # リソースの複数形名

# リソース設定
RESOURCE_NAME=ansible-website        # 作成するリソース名
RESOURCE_NAMESPACE=hoge             # リソースの名前空間
```

### Ansibleワークフロー例

**標準的なワークフロー（uriベース）:**
```bash
# 1. イメージをビルド（初回のみ）
docker compose build

# 2. 環境を起動
docker compose up -d

# 3. YAMLファイル生成とCRDインストール
docker compose exec kubectl-proxy ./scripts/manage-crd.sh generate
docker compose exec kubectl-proxy kubectl apply -f /src/crd-website-generated.yaml
docker compose exec kubectl-proxy kubectl apply -f /src/namespace-generated.yaml

# 4. Ansibleでカスタムリソースを作成（uriベース）
docker compose exec ansible ansible-playbook create-custom-resources.yml

# 5. 作成されたリソースを確認
docker compose exec kubectl-proxy kubectl get websites -n hoge

# 6. リソースの詳細を確認
docker compose exec kubectl-proxy kubectl describe website sample-website -n hoge

# 7. Ansibleでリソースを削除
docker compose exec ansible ansible-playbook delete-custom-resources.yml
```

**curlベースのワークフロー:**
```bash
# 1-3は同じ

# 4. Ansibleでカスタムリソースを作成（curlベース）
docker compose exec ansible ansible-playbook create-custom-resources-curl.yml

# 5-6は同じ

# 7. Ansibleでリソースを削除（curlベース）
docker compose exec ansible ansible-playbook delete-custom-resources-curl.yml
```

### Ansibleプレイブックの詳細

#### create-custom-resources.yml

このプレイブックは`uri`モジュールを使用してcurl相当のHTTP/HTTPS操作を実行します：

- **接続確認**: `/version`エンドポイントで接続テスト
- **名前空間管理**: GET/POSTリクエストで名前空間を作成
- **CRD確認**: CRDの存在を確認
- **リソース作成**: POSTリクエストでWebsiteリソースを作成
- **検証**: 作成したリソースの詳細を取得して表示

#### delete-custom-resources.yml

リソースの削除を行うシンプルなプレイブック：

- **存在確認**: GETリクエストでリソースの存在を確認
- **削除実行**: DELETEリクエストでリソースを削除

### Ansibleコンテナ内での作業

```bash
# Ansibleコンテナにシェル接続
docker compose exec ansible sh

# コンテナ内でプレイブック実行
cd /ansible
ansible-playbook create-custom-resources.yml

# 環境変数を確認
env | grep -E "PROXY|CRD|RESOURCE"

# コンテナから退出
exit
```

## HTTPS対応（統合モード）

kubectl-proxyはデフォルトでHTTPのみをサポートしていますが、このプロジェクトではHTTPS対応が統合されています。

### HTTPS有効化方法（統合アプローチ）

HTTP/HTTPS機能は単一のコンテナに統合されており、`ENABLE_HTTPS`環境変数で制御できます。

#### 1. HTTPS有効化して起動

```bash
# .envファイルでENABLE_HTTPS=trueを設定
echo "ENABLE_HTTPS=true" >> .env

# または、環境変数で直接指定して起動
ENABLE_HTTPS=true docker compose up -d
```

これにより以下のポートで接続可能になります：
- **HTTP**: ポート8001（常に利用可能）
- **HTTPS**: ポート8443（ENABLE_HTTPS=trueの場合のみ）

#### 2. 自己署名証明書の自動生成

HTTPS有効時、起動スクリプトは自動的に自己署名証明書を生成します：
- 証明書: `/tmp/certs/server.crt`
- 秘密鍵: `/tmp/certs/server.key`
- 有効期間: 365日
- CN: `kubectl-proxy`
- SAN: `DNS:kubectl-proxy,DNS:localhost,IP:127.0.0.1`

証明書は`socat`を使用してHTTPプロキシをHTTPSでラップすることで機能します。

#### 3. HTTPS接続の確認

```bash
# HTTPS経由でAPI情報を取得（証明書検証をスキップ）
curl -k https://localhost:8443/version

# Ansibleコンテナ内から接続
docker compose exec ansible sh
curl -k https://kubectl-proxy:8443/api/v1/namespaces
```

#### 4. AnsibleでHTTPS接続を使用

Playbookは`ENABLE_HTTPS`環境変数を検出し、自動的にHTTPS接続に切り替わります：

```bash
# ENABLE_HTTPS=trueの場合、自動的にhttps://kubectl-proxy:8443に接続
docker compose exec ansible ansible-playbook create-custom-resources.yml

# または明示的にHTTPS設定で実行
docker compose exec \
  -e ENABLE_HTTPS=true \
  ansible ansible-playbook create-custom-resources-curl.yml
```

**手動設定（オプション）:**

.envファイルで手動設定することも可能：

```env
ENABLE_HTTPS=true
HTTPS_PORT=8443
PROXY_PROTOCOL=https
PROXY_PORT=8443
```

### HTTPS技術詳細

- **実装方法**: `socat`を使用してHTTPプロキシをHTTPSでラップ（単一コンテナ内で動作）
- **証明書**: `generate-certs.sh`スクリプトでOpenSSLにより自動生成
- **プロセス構成**: 
  - `kubectl proxy`がHTTPで8001ポートをリッスン
  - `socat`がHTTPSで8443ポートをリッスンし、127.0.0.1:8001に転送
- **セキュリティ**: 開発・テスト環境向け。本番環境では信頼された証明書を使用してください

### HTTPSの有効化・無効化

```bash
# HTTPのみ（デフォルト）
docker compose up -d

# HTTPSを有効化
ENABLE_HTTPS=true docker compose up -d

# 設定変更後は再起動が必要
docker compose restart kubectl-proxy

# すべて停止
docker compose down
```

### 環境変数での設定

.env.exampleから.envを作成し、以下を設定：

```env
# HTTPS設定
ENABLE_HTTPS=true
HTTPS_PORT=8443
CERT_DIR=/tmp/certs

# Ansible用HTTPS接続設定
PROXY_URL=https://kubectl-proxy-https:8443
PROXY_PROTOCOL=https
```