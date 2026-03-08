#!/usr/bin/env bash
# deploy-test-lambda.sh
# テスト用Lambda関数（test_parallel_api / test_multi_thread_api）を
# 作成または更新するスクリプト
#
# 使用方法:
#   bash scripts/deploy-test-lambda.sh [オプション]
#
# オプション:
#   --region        AWSリージョン（デフォルト: ap-northeast-1）
#   --stack-name    CloudFormationスタック名（デフォルト: openapi-cognito-auth-dev）
#   --project-name  プロジェクト名（デフォルト: openapi-cognito-auth）
#   --env           環境名（デフォルト: dev）
#   --role-arn      Lambda実行ロールARN（省略時はスタックから自動取得）
#   --help          このヘルプを表示
#
# 必要なIAM権限（実行者）:
#   lambda:CreateFunction, lambda:UpdateFunctionCode,
#   lambda:UpdateFunctionConfiguration, lambda:GetFunction,
#   iam:PassRole

set -euo pipefail

# ─────────────────────────────────────────────
# デフォルト値
# ─────────────────────────────────────────────
REGION="ap-northeast-1"
STACK_NAME="openapi-cognito-auth-dev"
PROJECT_NAME="openapi-cognito-auth"
ENV="dev"
ROLE_ARN=""

# ─────────────────────────────────────────────
# 引数パース
# ─────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --region)       REGION="$2";       shift 2 ;;
        --stack-name)   STACK_NAME="$2";   shift 2 ;;
        --project-name) PROJECT_NAME="$2"; shift 2 ;;
        --env)          ENV="$2";          shift 2 ;;
        --role-arn)     ROLE_ARN="$2";     shift 2 ;;
        --help)
            sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "不明なオプション: $1" >&2
            exit 1
            ;;
    esac
done

# ─────────────────────────────────────────────
# スクリプトのディレクトリ基準でパスを解決
# ─────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAMBDA_DIR="${SCRIPT_DIR}/lambda"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

echo "=== テスト用Lambda関数デプロイ ==="
echo "リージョン     : ${REGION}"
echo "スタック名     : ${STACK_NAME}"
echo "プロジェクト名 : ${PROJECT_NAME}"
echo "環境           : ${ENV}"

# ─────────────────────────────────────────────
# AWS CLI の疎通確認
# ─────────────────────────────────────────────
ACCOUNT_ID="$(aws sts get-caller-identity --query 'Account' --output text 2>&1)" || {
    echo "エラー: AWS CLI が設定されていないか、認証情報が無効です。" >&2
    exit 1
}
echo "AWSアカウントID: ${ACCOUNT_ID}"

# ─────────────────────────────────────────────
# 実行ロールARNの解決
# （省略時はスタックの BackendLambdaRole を流用）
# ─────────────────────────────────────────────
if [[ -z "${ROLE_ARN}" ]]; then
    echo "実行ロールをCloudFormationスタックから取得中..."
    ROLE_ARN="$(aws cloudformation describe-stack-resources \
        --stack-name "${STACK_NAME}" \
        --query "StackResources[?ResourceType=='AWS::IAM::Role' && LogicalResourceId=='BackendLambdaRole'].PhysicalResourceId" \
        --output text \
        --region "${REGION}" 2>/dev/null)" || true

    if [[ -z "${ROLE_ARN}" || "${ROLE_ARN}" == "None" ]]; then
        echo "エラー: 実行ロールが見つかりませんでした。--role-arn で指定してください。" >&2
        exit 1
    fi
    # 物理IDがロール名のときARNに変換
    if [[ "${ROLE_ARN}" != arn:* ]]; then
        ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_ARN}"
    fi
fi
echo "実行ロールARN  : ${ROLE_ARN}"

# ─────────────────────────────────────────────
# デプロイ対象の Lambda 定義
#   FORMAT: "論理名:ファイル名:ハンドラ名:説明"
# ─────────────────────────────────────────────
LAMBDAS=(
    "${PROJECT_NAME}-test-parallel-${ENV}:test_parallel_api.py:test_parallel_api.lambda_handler:並列アクセス性能比較（sequential/multi_session/multi_process）"
    "${PROJECT_NAME}-test-multi-thread-${ENV}:test_multi_thread_api.py:test_multi_thread_api.lambda_handler:マルチスレッド並列アクセステスト"
)

# ─────────────────────────────────────────────
# 関数ごとにデプロイ
# ─────────────────────────────────────────────
for LAMBDA_DEF in "${LAMBDAS[@]}"; do
    FUNC_NAME="$(echo "${LAMBDA_DEF}" | cut -d: -f1)"
    SOURCE_FILE="$(echo "${LAMBDA_DEF}" | cut -d: -f2)"
    HANDLER="$(echo "${LAMBDA_DEF}" | cut -d: -f3)"
    DESCRIPTION="$(echo "${LAMBDA_DEF}" | cut -d: -f4)"

    SOURCE_PATH="${LAMBDA_DIR}/${SOURCE_FILE}"
    if [[ ! -f "${SOURCE_PATH}" ]]; then
        echo "警告: ${SOURCE_PATH} が見つかりません。スキップします。" >&2
        continue
    fi

    # zip パッケージ作成
    ZIP_PATH="${WORK_DIR}/${FUNC_NAME}.zip"
    (cd "${LAMBDA_DIR}" && zip -j "${ZIP_PATH}" "${SOURCE_FILE}" > /dev/null)
    echo ""
    echo "--- ${FUNC_NAME} ---"
    echo "ソース   : ${SOURCE_PATH}"
    echo "ハンドラ : ${HANDLER}"

    # 関数が既存かどうか確認
    if aws lambda get-function --function-name "${FUNC_NAME}" --region "${REGION}" \
            --query 'Configuration.FunctionName' --output text &>/dev/null; then
        # 既存 → コードと設定を更新
        echo "既存の関数を更新中..."
        aws lambda update-function-code \
            --function-name "${FUNC_NAME}" \
            --zip-file "fileb://${ZIP_PATH}" \
            --region "${REGION}" \
            --output json \
            --query '{FunctionName:FunctionName,CodeSize:CodeSize,LastModified:LastModified}' \
            | cat
        # ハンドラ・説明も最新に合わせる
        aws lambda update-function-configuration \
            --function-name "${FUNC_NAME}" \
            --handler "${HANDLER}" \
            --description "${DESCRIPTION}" \
            --region "${REGION}" \
            --output json \
            --query '{FunctionName:FunctionName,Handler:Handler}' \
            | cat
        echo "✓ ${FUNC_NAME} を更新しました"
    else
        # 新規作成
        echo "新規作成中..."
        aws lambda create-function \
            --function-name "${FUNC_NAME}" \
            --runtime python3.12 \
            --handler "${HANDLER}" \
            --role "${ROLE_ARN}" \
            --zip-file "fileb://${ZIP_PATH}" \
            --description "${DESCRIPTION}" \
            --timeout 300 \
            --memory-size 256 \
            --region "${REGION}" \
            --output json \
            --query '{FunctionName:FunctionName,FunctionArn:FunctionArn,Runtime:Runtime}' \
            | cat
        echo "✓ ${FUNC_NAME} を作成しました"
        echo ""
        echo "  次の手順: Lambda コンソールで以下の環境変数を設定してください。"
        echo "    API_ENDPOINT  = https://<API_ID>.execute-api.${REGION}.amazonaws.com/dev"
        echo "    USER_POOL_ID  = ${REGION}_XXXXXXXXX"
        echo "    CLIENT_ID     = <CLIENT_ID>"
        echo "    USERNAME      = <TEST_USERNAME>"
        echo "    PASSWORD      = <TEST_PASSWORD>"
    fi
done

echo ""
echo "=== デプロイ完了 ==="
