#!/usr/bin/env bash
# invoke-test-lambda.sh
# テスト用Lambda関数（test_parallel_api）を
# AWS CLI で非同期または同期実行するスクリプト
#
# 使用方法:
#   bash scripts/invoke-test-lambda.sh [オプション]
#
# オプション:
#   --function      実行する関数を選択: parallel（デフォルト: parallel）
#   --region        AWSリージョン（デフォルト: ap-northeast-1）
#   --project-name  プロジェクト名（デフォルト: openapi-cognito-auth）
#   --env           環境名（デフォルト: dev）
#   --endpoint      API Gatewayエンドポイント（必須または環境変数 API_ENDPOINT）
#   --user-pool-id  Cognito User Pool ID（必須または環境変数 USER_POOL_ID）
#   --client-id     Cognito クライアントID（必須または環境変数 CLIENT_ID）
#   --username      テストユーザー名（必須または環境変数 LAMBDA_USERNAME）
#   --password      テストユーザーパスワード（必須または環境変数 LAMBDA_PASSWORD）
#   --num-requests  リクエスト数（デフォルト: 20）
#   --num-workers   スレッド/プロセス数（デフォルト: 5）
#   --approaches    アプローチ一覧（parallel関数のみ有効。デフォルト: sequential,multi_session,multi_process）
#   --async         RequestResponse の代わりに Event（非同期）で呼び出す
#   --help          このヘルプを表示
#
# 必要なIAM権限（実行者）:
#   lambda:InvokeFunction

set -euo pipefail

# ─────────────────────────────────────────────
# デフォルト値
# ─────────────────────────────────────────────
FUNCTION="parallel"
REGION="ap-northeast-1"
PROJECT_NAME="openapi-cognito-auth"
ENV="dev"
ENDPOINT="${API_ENDPOINT:-}"
USER_POOL_ID="${USER_POOL_ID:-}"
CLIENT_ID="${CLIENT_ID:-}"
USERNAME="${LAMBDA_USERNAME:-}"
PASSWORD="${LAMBDA_PASSWORD:-}"
NUM_REQUESTS="20"
NUM_WORKERS="5"
APPROACHES="sequential,multi_session,multi_process"
INVOCATION_TYPE="RequestResponse"

# ─────────────────────────────────────────────
# 引数パース
# ─────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --function)      FUNCTION="$2";      shift 2 ;;
        --region)        REGION="$2";        shift 2 ;;
        --project-name)  PROJECT_NAME="$2";  shift 2 ;;
        --env)           ENV="$2";           shift 2 ;;
        --endpoint)      ENDPOINT="$2";      shift 2 ;;
        --user-pool-id)  USER_POOL_ID="$2";  shift 2 ;;
        --client-id)     CLIENT_ID="$2";     shift 2 ;;
        --username)      USERNAME="$2";      shift 2 ;;
        --password)      PASSWORD="$2";      shift 2 ;;
        --num-requests)  NUM_REQUESTS="$2";  shift 2 ;;
        --num-workers)   NUM_WORKERS="$2";   shift 2 ;;
        --approaches)    APPROACHES="$2";    shift 2 ;;
        --async)         INVOCATION_TYPE="Event"; shift ;;
        --help)
            sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "不明なオプション: $1" >&2
            exit 1
            ;;
    esac
done

# ─────────────────────────────────────────────
# 必須パラメータの確認
# ─────────────────────────────────────────────
MISSING=()
[[ -z "${ENDPOINT}" ]]      && MISSING+=("--endpoint / API_ENDPOINT")
[[ -z "${USER_POOL_ID}" ]]  && MISSING+=("--user-pool-id / USER_POOL_ID")
[[ -z "${CLIENT_ID}" ]]     && MISSING+=("--client-id / CLIENT_ID")
[[ -z "${USERNAME}" ]]      && MISSING+=("--username / LAMBDA_USERNAME")
[[ -z "${PASSWORD}" ]]      && MISSING+=("--password / LAMBDA_PASSWORD")

if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "エラー: 以下の必須パラメータが指定されていません:" >&2
    for m in "${MISSING[@]}"; do echo "  ${m}" >&2; done
    echo "" >&2
    echo "使用例:" >&2
    echo "  bash scripts/invoke-test-lambda.sh \\" >&2
    echo "    --endpoint  https://<API_ID>.execute-api.ap-northeast-1.amazonaws.com/dev \\" >&2
    echo "    --user-pool-id ap-northeast-1_XXXXXXXXX \\" >&2
    echo "    --client-id    <CLIENT_ID> \\" >&2
    echo "    --username     testuser \\" >&2
    echo "    --password     'TempPass123!'" >&2
    exit 1
fi

# ─────────────────────────────────────────────
# AWS CLI の疎通確認
# ─────────────────────────────────────────────
ACCOUNT_ID="$(aws sts get-caller-identity --query 'Account' --output text)" || {
    echo "エラー: AWS CLI が設定されていないか、認証情報が無効です。" >&2
    exit 1
}

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

echo "=== テスト用Lambda関数 実行 ==="
echo "リージョン     : ${REGION}"
echo "プロジェクト名 : ${PROJECT_NAME}"
echo "環境           : ${ENV}"
echo "呼び出し方式   : ${INVOCATION_TYPE}"
echo "AWSアカウントID: ${ACCOUNT_ID}"
echo ""

# ─────────────────────────────────────────────
# 関数呼び出しヘルパー
# ─────────────────────────────────────────────
invoke_lambda() {
    local func_name="$1"
    local payload="$2"
    local out_file="${WORK_DIR}/${func_name}.json"

    echo "--- ${func_name} ---"
    echo "ペイロード:"
    echo "${payload}" | python3 -m json.tool 2>/dev/null || echo "${payload}"
    echo ""

    # Lambda を呼び出す
    local http_status
    http_status="$(aws lambda invoke \
        --function-name "${func_name}" \
        --invocation-type "${INVOCATION_TYPE}" \
        --payload "${payload}" \
        --region "${REGION}" \
        --cli-binary-format raw-in-base64-out \
        --output json \
        --query 'StatusCode' \
        "${out_file}")" || {
        echo "エラー: Lambda の呼び出しに失敗しました（関数名: ${func_name}）" >&2
        return 1
    }

    echo "HTTPステータスコード: ${http_status}"

    if [[ "${INVOCATION_TYPE}" == "RequestResponse" && -f "${out_file}" ]]; then
        echo "レスポンス:"
        python3 -c "
import json, sys
raw = open('${out_file}').read()
try:
    obj = json.loads(raw)
    # body が文字列の場合はさらにパース
    if isinstance(obj.get('body'), str):
        obj['body'] = json.loads(obj['body'])
    print(json.dumps(obj, ensure_ascii=False, indent=2))
except Exception:
    print(raw)
"
    fi
    echo ""
}

# ─────────────────────────────────────────────
# 並列アクセス性能比較 Lambda（test_parallel_api）
# ─────────────────────────────────────────────
invoke_parallel() {
    local func_name="${PROJECT_NAME}-test-parallel-${ENV}"
    local payload
    payload="$(python3 -c "
import json
print(json.dumps({
    'API_ENDPOINT':  '${ENDPOINT}',
    'USER_POOL_ID':  '${USER_POOL_ID}',
    'CLIENT_ID':     '${CLIENT_ID}',
    'USERNAME':      '${USERNAME}',
    'PASSWORD':      '${PASSWORD}',
    'NUM_REQUESTS':  '${NUM_REQUESTS}',
    'NUM_WORKERS':   '${NUM_WORKERS}',
    'APPROACHES':    '${APPROACHES}',
}))")"
    invoke_lambda "${func_name}" "${payload}"
}

# ─────────────────────────────────────────────
# 実行
# ─────────────────────────────────────────────
case "${FUNCTION}" in
    parallel)
        invoke_parallel
        ;;
    *)
        echo "エラー: --function には parallel を指定してください。" >&2
        exit 1
        ;;
esac

echo "=== 実行完了 ==="
