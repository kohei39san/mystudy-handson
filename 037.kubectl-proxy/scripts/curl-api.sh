#!/bin/sh
# kubectl proxy経由でcurlを使用したKubernetes API操作スクリプト

set -e

# .envファイルを読み込み（存在する場合）
if [ -f "/.env" ]; then
    echo ".envファイルを読み込み中..."
    export $(grep -v '^#' /.env | grep -v '^$' | xargs)
    echo "✓ 環境変数を読み込みました"
else
    echo "❌ .envファイルが見つかりません: /.env"
    echo "docker-compose.ymlで.envファイルがマウントされているか確認してください"
fi

ACTION=${1:-help}
PROXY_URL="http://kubectl-proxy:8001"

show_help() {
    echo "curl API操作コマンド:"
    echo "  ./curl-api.sh api-info           - API情報を取得"
    echo "  ./curl-api.sh list-namespaces    - 名前空間一覧"
    echo "  ./curl-api.sh get-namespace      - 特定の名前空間情報"
    echo "  ./curl-api.sh create-namespace   - 名前空間作成（生成ファイル使用）"
    echo "  ./curl-api.sh delete-namespace   - 名前空間削除"
    echo "  ./curl-api.sh list-crds          - CRD一覧"
    echo "  ./curl-api.sh get-crd            - Website CRDの詳細"
    echo "  ./curl-api.sh list-websites      - Websiteリソース一覧"
    echo "  ./curl-api.sh get-website <name> - 特定のWebsiteリソース取得"
    echo "  ./curl-api.sh create-website     - サンプルWebsiteリソース作成（生成ファイル使用）"
    echo "  ./curl-api.sh delete-website <name> - Websiteリソース削除"
    echo "  ./curl-api.sh patch-website <name>  - Websiteリソース更新"
    echo "  ./curl-api.sh watch-websites     - Websiteリソースをwatch"
    echo "  ./curl-api.sh api-resources      - 利用可能APIリソース一覧"
    echo "  ./curl-api.sh help               - このヘルプを表示"
}

# APIサーバー情報を取得
get_api_info() {
    echo "=== Kubernetes API情報 ==="
    curl -s "${PROXY_URL}/version" | jq '.'
    echo ""
    
    echo "=== API Groups ==="
    curl -s "${PROXY_URL}/api" | jq '.versions'
    echo ""
    
    echo "=== Extensions API Groups ==="
    curl -s "${PROXY_URL}/apis" | jq '.groups[].name' | head -10
}

# 名前空間一覧
list_namespaces() {
    echo "=== 名前空間一覧 ==="
    curl -s "${PROXY_URL}/api/v1/namespaces" | \
    jq -r '.items[] | "\(.metadata.name) \t\(.status.phase) \t\(.metadata.creationTimestamp)"' | \
    column -t -s $'\t'
}

# 特定の名前空間情報
get_namespace() {
    echo "=== 名前空間 '${RESOURCE_NAMESPACE}' の詳細 ==="
    curl -s "${PROXY_URL}/api/v1/namespaces/${RESOURCE_NAMESPACE}" | jq '.'
}

# 名前空間作成（生成ファイル使用）
create_namespace() {
    echo "=== 名前空間 '${RESOURCE_NAMESPACE}' を作成 ==="
    
    # 生成されたファイルが存在するかチェック
    if [ ! -f "/src/namespace-generated.yaml" ]; then
        echo "❌ 生成されたnamespaceファイルが見つかりません"
        echo "最初に './scripts/manage-crd.sh generate' を実行してください"
        return 1
    fi
    
    # 生成されたファイルをそのまま使用
    echo "生成されたファイルをそのまま使用して名前空間を作成..."
    
    curl -s -X POST \
        "${PROXY_URL}/api/v1/namespaces" \
        -H "Content-Type: application/yaml" \
        -d @/src/namespace-generated.yaml
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ 名前空間（生成ファイル使用）が作成されました"
    fi
}

# 名前空間削除
delete_namespace() {
    echo "=== 名前空間 '${RESOURCE_NAMESPACE}' を削除 ==="
    
    curl -s -X DELETE \
        "${PROXY_URL}/api/v1/namespaces/${RESOURCE_NAMESPACE}"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ 名前空間 '${RESOURCE_NAMESPACE}' が削除されました"
    fi
}

# CRD一覧
list_crds() {
    echo "=== CRD一覧 ==="
    curl -s "${PROXY_URL}/apis/apiextensions.k8s.io/v1/customresourcedefinitions" | \
    jq -r '.items[] | "\(.metadata.name) \t\(.spec.group) \t\(.spec.versions[0].name)"' | \
    column -t -s $'\t'
}

# Website CRDの詳細
get_crd() {
    echo "=== Website CRD詳細 ==="
    curl -s "${PROXY_URL}/apis/apiextensions.k8s.io/v1/customresourcedefinitions/${CRD_PLURAL}.${CRD_GROUP}" | \
    jq '{
        name: .metadata.name,
        group: .spec.group,
        versions: .spec.versions[].name,
        scope: .spec.scope,
        names: .spec.names
    }'
}

# Websiteリソース一覧
list_websites() {
    echo "=== Websiteリソース一覧 (namespace: ${RESOURCE_NAMESPACE}) ==="
    curl -s "${PROXY_URL}/apis/${CRD_GROUP}/${CRD_VERSION}/namespaces/${RESOURCE_NAMESPACE}/${CRD_PLURAL}" | \
    jq -r '.items[] | "\(.metadata.name) \t\(.spec.url) \t\(.spec.environment) \t\(.status.phase // "N/A")"' | \
    column -t -s $'\t' || echo "リソースが見つかりません"
}

# 特定のWebsiteリソース取得
get_website() {
    local name=${1:-"sample-website"}
    echo "=== Websiteリソース '${name}' の詳細 ==="
    curl -s "${PROXY_URL}/apis/${CRD_GROUP}/${CRD_VERSION}/namespaces/${RESOURCE_NAMESPACE}/${CRD_PLURAL}/${name}" | jq '.'
}

# サンプルWebsiteリソース作成
create_website() {
    local name=${1:-"curl-test-website"}
    echo "=== Websiteリソース '${name}' を作成 ==="
    
    # 生成されたファイルが存在するかチェック
    if [ ! -f "/src/sample-websites-generated.yaml" ]; then
        echo "❌ 生成されたサンプルファイルが見つかりません"
        echo "最初に './scripts/manage-crd.sh generate' を実行してください"
        return 1
    fi
    
    # 生成されたファイルから最初のリソースを使用
    echo "生成されたファイルから最初のリソースを使用..."
    
    # 一時ファイルに最初のリソースを保存
    TEMP_FILE="/tmp/first-resource.yaml"
    
    # 生成されたYAMLから最初のリソース（---で区切られた最初の部分）を取得
    if grep -q "^---" /src/sample-websites-generated.yaml; then
        # 複数リソースがある場合は最初のリソースのみ取得
        awk 'BEGIN{print_flag=1} /^---/{print_flag=0} print_flag==1' /src/sample-websites-generated.yaml > "$TEMP_FILE"
    else
        # 単一リソースの場合はそのまま使用
        cp /src/sample-websites-generated.yaml "$TEMP_FILE"
    fi
    
    # YAMLをJSONに変換して送信
    yq eval -o=json "$TEMP_FILE" | curl -s -X POST \
        "${PROXY_URL}/apis/${CRD_GROUP}/${CRD_VERSION}/namespaces/${RESOURCE_NAMESPACE}/${CRD_PLURAL}" \
        -H "Content-Type: application/json" \
        -d @-
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Websiteリソース（生成ファイル使用）が作成されました"
    fi
}

# Websiteリソース削除
delete_website() {
    local name=${1:-"curl-test-website"}
    echo "=== Websiteリソース '${name}' を削除 ==="
    
    curl -s -X DELETE \
        "${PROXY_URL}/apis/${CRD_GROUP}/${CRD_VERSION}/namespaces/${RESOURCE_NAMESPACE}/${CRD_PLURAL}/${name}" | \
    jq '{status: .status, message: .message}'
    
    if [ $? -eq 0 ]; then
        echo "✓ Websiteリソース '${name}' の削除要求を送信しました"
    fi
}

# Websiteリソース更新（patch）
patch_website() {
    local name=${1:-"sample-website"}
    echo "=== Websiteリソース '${name}' を更新 ==="
    
    cat <<EOF | curl -s -X PATCH \
        "${PROXY_URL}/apis/${CRD_GROUP}/${CRD_VERSION}/namespaces/${RESOURCE_NAMESPACE}/${CRD_PLURAL}/${name}" \
        -H "Content-Type: application/merge-patch+json" \
        -d @-
{
    "spec": {
        "replicas": 5,
        "environment": "staging"
    },
    "status": {
        "phase": "Running",
        "conditions": [
            {
                "type": "Ready",
                "status": "True",
                "lastTransitionTime": "$(date -Iseconds)",
                "reason": "UpdatedViaCurl",
                "message": "Website updated via curl API"
            }
        ]
    }
}
EOF
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Websiteリソース '${name}' が更新されました"
    fi
}

# Websiteリソースをwatch
watch_websites() {
    echo "=== Websiteリソースの変更を監視 (Ctrl+Cで終了) ==="
    curl -s "${PROXY_URL}/apis/${CRD_GROUP}/${CRD_VERSION}/namespaces/${RESOURCE_NAMESPACE}/${CRD_PLURAL}?watch=true" | \
    while IFS= read -r line; do
        echo "$line" | jq -r '"\(.type): \(.object.metadata.name) - \(.object.spec.environment // "N/A")"'
    done
}

# 利用可能なAPIリソース一覧
get_api_resources() {
    echo "=== 利用可能なAPIリソース ==="
    curl -s "${PROXY_URL}/apis/${CRD_GROUP}/${CRD_VERSION}" | jq '.resources[]'
}

# 接続テスト
test_connection() {
    echo "kubectl proxy接続テスト..."
    if curl -s "${PROXY_URL}/version" > /dev/null; then
        echo "✓ kubectl proxyに接続できました"
        echo "Proxy URL: ${PROXY_URL}"
    else
        echo "❌ kubectl proxyに接続できません"
        echo "kubectl proxyが起動しているか確認してください"
        return 1
    fi
}

# メイン処理
# 接続テストを最初に実行
test_connection || exit 1

case "$ACTION" in
    "api-info")
        get_api_info
        ;;
    "list-namespaces")
        list_namespaces
        ;;
    "get-namespace")
        get_namespace
        ;;
    "create-namespace")
        create_namespace
        ;;
    "delete-namespace")
        delete_namespace
        ;;
    "list-crds")
        list_crds
        ;;
    "get-crd")
        get_crd
        ;;
    "list-websites")
        list_websites
        ;;
    "get-website")
        get_website "$2"
        ;;
    "create-website")
        create_website "$2"
        ;;
    "delete-website")
        delete_website "$2"
        ;;
    "patch-website")
        patch_website "$2"
        ;;
    "watch-websites")
        watch_websites
        ;;
    "api-resources")
        get_api_resources
        ;;
    "help")
        show_help
        ;;
    *)
        show_help
        ;;
esac