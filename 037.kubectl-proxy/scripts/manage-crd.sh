#!/bin/sh
# CRD管理用シェルスクリプト（kubectl-proxyコンテナ内で実行）

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
PROXY_URL="http://localhost:8001"

show_help() {
    echo "CRD管理コマンド:"
    echo "  ./manage-crd.sh generate         - テンプレートからYAMLファイルを生成"
    echo "  ./manage-crd.sh create-namespace - 名前空間を作成"
    echo "  ./manage-crd.sh delete-namespace - 名前空間を削除"
    echo "  ./manage-crd.sh install          - CRDをインストール"
    echo "  ./manage-crd.sh uninstall        - CRDをアンインストール"
    echo "  ./manage-crd.sh create-samples   - サンプルリソースを作成"
    echo "  ./manage-crd.sh delete-samples   - サンプルリソースを削除"
    echo "  ./manage-crd.sh list             - Websiteリソースを一覧表示"
    echo "  ./manage-crd.sh test-api         - kubectl proxy経由でAPIテスト"
    echo "  ./manage-crd.sh clean            - 生成されたファイルを削除"
    echo "  ./manage-crd.sh help             - このヘルプを表示"
}

generate_yaml() {
    echo "テンプレートからYAMLファイルを生成中..."
    
    # 環境変数が設定されているかチェック
    if [ -z "$CRD_GROUP" ] || [ -z "$CRD_KIND" ]; then
        echo "CRD環境変数が設定されていません"
        echo "docker-compose.ymlで.envファイルを読み込んでください"
        return 1
    fi
    
    # Namespace定義ファイルを生成
    echo "Namespace定義を生成: /src/namespace-generated.yaml"
    envsubst < /src/namespace-template.yaml > /src/namespace-generated.yaml
    
    # CRD定義ファイルを生成
    echo "CRD定義を生成: /src/crd-website-generated.yaml"
    envsubst < /src/crd-template.yaml > /src/crd-website-generated.yaml
    
    # カスタムリソースファイルを生成
    echo "サンプルリソースを生成: /src/sample-websites-generated.yaml"
    envsubst < /src/resource-template.yaml > /src/sample-websites-generated.yaml
    
    echo "✓ YAMLファイルの生成が完了しました"
    echo "生成されたファイル:"
    echo "  - /src/namespace-generated.yaml"
    echo "  - /src/crd-website-generated.yaml"
    echo "  - /src/sample-websites-generated.yaml"
}

clean_generated() {
    echo "生成されたファイルを削除中..."
    rm -f /src/namespace-generated.yaml /src/crd-website-generated.yaml /src/sample-websites-generated.yaml
    echo "✓ 生成されたファイルを削除しました"
}

install_crd() {
    echo "CRDをインストール中..."
    
    # 生成されたファイルをチェック
    if [ ! -f "/src/crd-website-generated.yaml" ]; then
        echo "❌ CRDファイルが見つかりません"
        echo "最初に './scripts/manage-crd.sh generate' を実行してください"
        return 1
    fi
    
    echo "生成されたCRDファイルを使用します"
    kubectl apply -f /src/crd-website-generated.yaml
    
    if [ $? -eq 0 ]; then
        echo "✓ CRDがインストールされました。"
        echo "確認: kubectl get crd websites.example.com"
    fi
}

create_namespace() {
    echo "名前空間を作成中..."
    
    # 生成されたファイルをチェック
    if [ ! -f "/src/namespace-generated.yaml" ]; then
        echo "❌ Namespaceファイルが見つかりません"
        echo "最初に './scripts/manage-crd.sh generate' を実行してください"
        return 1
    fi
    
    echo "生成されたNamespaceファイルを使用します"
    kubectl apply -f /src/namespace-generated.yaml
    
    if [ $? -eq 0 ]; then
        echo "✓ 名前空間 '${RESOURCE_NAMESPACE}' が作成されました。"
        echo "確認: kubectl get namespace ${RESOURCE_NAMESPACE}"
    fi
}

delete_namespace() {
    echo "名前空間を削除中..."
    
    # 名前空間の存在確認
    if ! kubectl get namespace "${RESOURCE_NAMESPACE}" >/dev/null 2>&1; then
        echo "名前空間 '${RESOURCE_NAMESPACE}' は存在しません"
        return 0
    fi
    
    echo "⚠️  警告: 名前空間 '${RESOURCE_NAMESPACE}' とその中のすべてのリソースが削除されます"
    echo "実行するには 'yes' と入力してください:"
    read -r confirmation
    
    if [ "$confirmation" = "yes" ]; then
        kubectl delete namespace "${RESOURCE_NAMESPACE}"
        if [ $? -eq 0 ]; then
            echo "✓ 名前空間 '${RESOURCE_NAMESPACE}' が削除されました。"
        fi
    else
        echo "キャンセルされました"
    fi
}

uninstall_crd() {
    echo "CRDをアンインストール中..."
    
    if [ ! -f "/src/crd-website-generated.yaml" ]; then
        echo "❌ CRDファイルが見つかりません"
        echo "CRDを手動で削除する場合: kubectl delete crd websites.example.com"
        return 1
    fi
    
    kubectl delete -f /src/crd-website-generated.yaml --ignore-not-found=true
    
    if [ $? -eq 0 ]; then
        echo "✓ CRDがアンインストールされました。"
    fi
}

create_samples() {
    echo "サンプルリソースを作成中..."
    
    if [ ! -f "/src/sample-websites-generated.yaml" ]; then
        echo "❌ サンプルファイルが見つかりません"
        echo "最初に './scripts/manage-crd.sh generate' を実行してください"
        return 1
    fi
    
    echo "生成されたサンプルファイルを使用します"
    kubectl apply -f /src/sample-websites-generated.yaml
    
    if [ $? -eq 0 ]; then
        echo "✓ サンプルリソースが作成されました。"
        echo "確認: kubectl get websites"
    fi
}

delete_samples() {
    echo "サンプルリソースを削除中..."
    
    if [ ! -f "/src/sample-websites-generated.yaml" ]; then
        echo "❌ サンプルファイルが見つかりません"
        echo "リソースを手動で削除する場合: kubectl delete websites --all"
        return 1
    fi
    
    kubectl delete -f /src/sample-websites-generated.yaml --ignore-not-found=true
    
    if [ $? -eq 0 ]; then
        echo "✓ サンプルリソースが削除されました。"
    fi
}

list_resources() {
    echo "=== Website CRD情報 ==="
    kubectl get crd websites.example.com -o wide 2>/dev/null || echo "CRDが見つかりません"
    
    echo ""
    echo "=== Websiteリソース一覧 ==="
    kubectl get websites -o wide 2>/dev/null || echo "Websiteリソースが見つかりません"
    
    echo ""
    echo "=== 詳細情報（sample-website） ==="
    kubectl describe website sample-website 2>/dev/null || echo "sample-websiteが見つかりません"
}

test_api() {
    echo "kubectl proxy経由でAPIをテスト中..."
    
    # プロキシの接続確認
    echo "1. プロキシ接続テスト..."
    if wget --quiet --tries=1 --spider "$PROXY_URL/api/v1" 2>/dev/null; then
        echo "✓ kubectl proxyに接続成功"
    else
        echo "✗ kubectl proxyに接続失敗"
        return 1
    fi
    
    echo ""
    echo "2. CRD API情報の取得..."
    if wget --quiet -O - "$PROXY_URL/apis/example.com/v1" 2>/dev/null | grep -q "groupVersion"; then
        echo "✓ CRD APIに接続成功"
        echo "API Group: example.com/v1"
        wget --quiet -O - "$PROXY_URL/apis/example.com/v1" 2>/dev/null | grep -o '"name":"[^"]*"' | head -5
    else
        echo "✗ CRD APIアクセス失敗（CRDがインストールされていない可能性）"
    fi
    
    echo ""
    echo "3. Websiteリソース一覧の取得..."
    if WEBSITES=$(wget --quiet -O - "$PROXY_URL/apis/example.com/v1/namespaces/default/websites" 2>/dev/null); then
        echo "✓ Websiteリソース取得成功"
        ITEM_COUNT=$(echo "$WEBSITES" | grep -o '"name":"[^"]*"' | wc -l)
        if [ "$ITEM_COUNT" -gt 0 ]; then
            echo "Websites ($ITEM_COUNT 個):"
            echo "$WEBSITES" | grep -o '"name":"[^"]*"' | sed 's/"name":"/  - /' | sed 's/"//'
        else
            echo "  Websiteリソースが見つかりません"
        fi
    else
        echo "✗ Websiteリソース取得失敗"
    fi
    
    echo ""
    echo "4. 特定リソースの詳細取得..."
    if WEBSITE=$(wget --quiet -O - "$PROXY_URL/apis/example.com/v1/namespaces/default/websites/sample-website" 2>/dev/null); then
        echo "✓ sample-website詳細取得成功"
        URL=$(echo "$WEBSITE" | grep -o '"url":"[^"]*"' | sed 's/"url":"//' | sed 's/"//')
        REPLICAS=$(echo "$WEBSITE" | grep -o '"replicas":[0-9]*' | sed 's/"replicas"://')
        echo "URL: $URL"
        echo "Replicas: $REPLICAS"
    else
        echo "✗ sample-website詳細取得失敗"
    fi
    
    echo ""
    echo "=== APIテスト完了 ==="
}

# メイン処理
case "$ACTION" in
    "generate")
        generate_yaml
        ;;
    "create-namespace")
        create_namespace
        ;;
    "delete-namespace")
        delete_namespace
        ;;
    "install")
        install_crd
        ;;
    "uninstall")
        uninstall_crd
        ;;
    "create-samples")
        create_samples
        ;;
    "delete-samples")
        delete_samples
        ;;
    "list")
        list_resources
        ;;
    "test-api")
        test_api
        ;;
    "clean")
        clean_generated
        ;;
    "help")
        show_help
        ;;
    *)
        show_help
        ;;
esac