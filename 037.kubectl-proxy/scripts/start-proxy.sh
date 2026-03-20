#!/bin/sh
set -e  # エラー発生時に停止
set -x  # 実行コマンドを表示

# .envファイルがマウントされている場合は読み込み（オプション）
if [ -f "/.env" ]; then
    echo "Loading .env file..."
    set -a  # 変数をエクスポートに設定
    . /.env
    set +a  # エクスポート設定を解除
fi

# 環境変数のデフォルト値設定
HOME=${HOME:-"/tmp"}
PROXY_ADDRESS=${PROXY_ADDRESS:-"0.0.0.0"}
PROXY_PORT=${PROXY_PORT:-"8001"}
ACCEPT_HOSTS=${ACCEPT_HOSTS:-".*"}
LOG_LEVEL=${LOG_LEVEL:-"2"}
K8S_ORIGINAL_SERVER=${K8S_ORIGINAL_SERVER:-"https://127.0.0.1:55420"}
K8S_TARGET_SERVER=${K8S_TARGET_SERVER:-"https://host.docker.internal:55420"}
INSECURE_SKIP_TLS=${INSECURE_SKIP_TLS:-"true"}
KUBECONFIG_DIR=${KUBECONFIG_DIR:-"/tmp/.kube"}

setup_shell_helpers() {
    mkdir -p "${HOME}"

    cat > "${HOME}/.shrc" <<'EOF'
alias k='kubectl'

# For plain interactive `sh`, hand off to bash to get reliable programmable
# completion behavior while keeping `sh -c` semantics untouched.
if [ -n "${PS1:-}" ] && [ -z "${BASH_EXECUTION_STRING:-}" ] && [ "${0##*/}" = "sh" ] && [ -z "${KUBECTL_SH_BASH_HANDOFF:-}" ]; then
    export KUBECTL_SH_BASH_HANDOFF=1
    exec bash -i
fi

# Show candidate list on double-tab when completion is ambiguous.
bind 'set show-all-if-ambiguous on' 2>/dev/null || true

if command -v kubectl >/dev/null 2>&1; then
    if command -v complete >/dev/null 2>&1; then
        # kubectl completion expects this helper from bash-completion.
        # Define a minimal compatible version for sh sessions.
        if ! command -v _get_comp_words_by_ref >/dev/null 2>&1; then
            _get_comp_words_by_ref() {
                local __cur __prev __cword
                local -a __words

                if [ "$1" = "-n" ]; then
                    shift 2
                fi

                __words=("${COMP_WORDS[@]}")
                __cword=${COMP_CWORD:-0}
                __cur=${COMP_WORDS[__cword]}
                __prev=""
                if [ "${__cword}" -gt 0 ]; then
                    __prev=${COMP_WORDS[$((__cword - 1))]}
                fi

                while [ "$#" -gt 0 ]; do
                    case "$1" in
                        cur)
                            cur=${__cur}
                            ;;
                        prev)
                            prev=${__prev}
                            ;;
                        words)
                            words=("${__words[@]}")
                            ;;
                        cword)
                            cword=${__cword}
                            ;;
                    esac
                    shift
                done
            }
        fi

        KUBECTL_COMPLETION_FILE="/tmp/.kubectl-completion.sh"
        if kubectl completion bash > "${KUBECTL_COMPLETION_FILE}" 2>/dev/null; then
            . "${KUBECTL_COMPLETION_FILE}"
            complete -o default -F __start_kubectl k
        fi
    fi
fi
EOF

    cp "${HOME}/.shrc" "${HOME}/.bashrc"

    echo "Shell helpers configured in ${HOME}/.shrc"
    echo "  alias: k=kubectl"
    echo "  completion: enabled when shell supports 'complete' builtin"
}

echo "=== kubectl proxy startup script ==="
echo "Configuration:"
echo "  HOME: $HOME"
echo "  PROXY_ADDRESS: $PROXY_ADDRESS"
echo "  PROXY_PORT: $PROXY_PORT"
echo "  ACCEPT_HOSTS: $ACCEPT_HOSTS"
echo "  LOG_LEVEL: $LOG_LEVEL"
echo "  K8S_ORIGINAL_SERVER: $K8S_ORIGINAL_SERVER"
echo "  K8S_TARGET_SERVER: $K8S_TARGET_SERVER"
echo "  INSECURE_SKIP_TLS: $INSECURE_SKIP_TLS"
echo "  KUBECONFIG_DIR: $KUBECONFIG_DIR"
echo "0. Setting up interactive shell helpers..."
setup_shell_helpers
echo "1. Creating .kube directory..."
mkdir -p ${KUBECONFIG_DIR}
#chmod 755 ${KUBECONFIG_DIR}
#chown root:root ${KUBECONFIG_DIR}

echo "2. Checking original kubeconfig..."
ls -la /original-kubeconfig

echo "3. Checking .kube directory permissions..."
ls -ld ${KUBECONFIG_DIR}
id

echo "4. Creating modified kubeconfig..."
if [ "$INSECURE_SKIP_TLS" = "true" ]; then
    sed "s|$K8S_ORIGINAL_SERVER|$K8S_TARGET_SERVER|g" /original-kubeconfig | \
    sed '/insecure-skip-tls-verify/d' | \
    sed '/certificate-authority-data/d' | \
    sed "s|server: $K8S_TARGET_SERVER|server: $K8S_TARGET_SERVER\\n    insecure-skip-tls-verify: true|" > ${KUBECONFIG_DIR}/config
else
    sed "s|$K8S_ORIGINAL_SERVER|$K8S_TARGET_SERVER|g" /original-kubeconfig > ${KUBECONFIG_DIR}/config
fi

# kubeconfigファイルの権限を設定
#chmod 600 ${KUBECONFIG_DIR}/config
#chown root:root ${KUBECONFIG_DIR}/config

# KUBECONFIG環境変数を設定
export KUBECONFIG=${KUBECONFIG_DIR}/config

echo "5. Verifying created kubeconfig..."
ls -la ${KUBECONFIG_DIR}/config
head -n 20 ${KUBECONFIG_DIR}/config

echo "6. Testing kubectl connection..."
KUBECTL_ARGS="--request-timeout=10s"
if [ "$INSECURE_SKIP_TLS" = "true" ]; then
    KUBECTL_ARGS="$KUBECTL_ARGS --insecure-skip-tls-verify"
fi
kubectl cluster-info $KUBECTL_ARGS

echo "6. Starting kubectl proxy..."
PROXY_ARGS="--address=$PROXY_ADDRESS --port=$PROXY_PORT --accept-hosts=$ACCEPT_HOSTS --v=$LOG_LEVEL"
if [ "$INSECURE_SKIP_TLS" = "true" ]; then
    PROXY_ARGS="$PROXY_ARGS --insecure-skip-tls-verify"
fi
exec kubectl proxy $PROXY_ARGS