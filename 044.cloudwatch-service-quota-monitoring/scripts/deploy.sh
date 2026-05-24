#!/bin/bash
# Service Quotas Automatic Management + AWS User Notifications deployment script

set -euo pipefail

STACK_NAME="${STACK_NAME:-service-quota-monitoring}"
STACKSET_NAME="${STACKSET_NAME:-service-quota-monitoring}"
TEMPLATE_FILE="$(dirname "$0")/../cfn/stackset-template.yaml"
REGION="${AWS_DEFAULT_REGION:-ap-northeast-1}"

SERVICE_QUOTA_NOTIFICATION_NAME="${SERVICE_QUOTA_NOTIFICATION_NAME:-service-quota-auto-management}"
SERVICE_QUOTA_NOTIFICATION_DESCRIPTION="${SERVICE_QUOTA_NOTIFICATION_DESCRIPTION:-Notifications for Service Quotas Automatic Management}"
SERVICE_QUOTA_AGGREGATION_DURATION="${SERVICE_QUOTA_AGGREGATION_DURATION:-SHORT}"
SERVICE_QUOTA_SLACK_CHANNEL_ARN="${SERVICE_QUOTA_SLACK_CHANNEL_ARN:-}"

AUTO_MANAGEMENT_OPT_IN_LEVEL="${AUTO_MANAGEMENT_OPT_IN_LEVEL:-ACCOUNT}"
AUTO_MANAGEMENT_OPT_IN_TYPE="${AUTO_MANAGEMENT_OPT_IN_TYPE:-NotifyOnly}"
AUTO_MANAGEMENT_NOTIFICATION_ARN="${AUTO_MANAGEMENT_NOTIFICATION_ARN:-}"
AUTO_MANAGEMENT_EXCLUSION_LIST="${AUTO_MANAGEMENT_EXCLUSION_LIST:-}"

usage() {
    cat <<EOF
使用方法:
  $0 <command> [options]

コマンド:
  deploy-stack      CloudFormation スタックとしてデプロイ（単一アカウント）
  deploy-stackset   CloudFormation StackSet としてデプロイ（複数アカウント/リージョン）
  add-instances     StackSet インスタンスを追加（deploy-stackset 実行後）
    enable-auto-management Service Quotas 自動管理(NotifyOnly)を有効化/更新
    show-auto-management   Service Quotas 自動管理の現在設定を表示
  delete-stack      スタックを削除
  delete-stackset   StackSet を削除
  status            スタックのステータスを確認
  validate          テンプレートを検証

環境変数:
  STACK_NAME                          スタック名 (デフォルト: service-quota-monitoring)
  STACKSET_NAME                       StackSet 名 (デフォルト: service-quota-monitoring)
  AWS_DEFAULT_REGION                  デプロイ先リージョン (デフォルト: ap-northeast-1)
    SERVICE_QUOTA_NOTIFICATION_NAME     User Notifications 設定名
    SERVICE_QUOTA_NOTIFICATION_DESCRIPTION User Notifications 設定の説明
    SERVICE_QUOTA_AGGREGATION_DURATION  User Notifications 集約期間 (SHORT|LONG)
    SERVICE_QUOTA_SLACK_CHANNEL_ARN     Slack チャネル ARN (任意)
    AUTO_MANAGEMENT_OPT_IN_LEVEL        start/update-auto-management の opt-in-level (デフォルト: ACCOUNT)
    AUTO_MANAGEMENT_OPT_IN_TYPE         start/update-auto-management の opt-in-type (デフォルト: NotifyOnly)
    AUTO_MANAGEMENT_NOTIFICATION_ARN    自動管理に紐付ける通知ARN。未指定時はスタック出力から取得
    AUTO_MANAGEMENT_EXCLUSION_LIST      除外リスト(JSON文字列, 任意)

例:
  # 単一アカウントへのデプロイ
  $0 deploy-stack

  # User Notifications + Slack連携を作成
  AWS_DEFAULT_REGION=ap-northeast-1 \
  SERVICE_QUOTA_SLACK_CHANNEL_ARN=arn:aws:chatbot:us-east-1:123456789012:chat-configuration/slack-channel/my-channel \
  $0 deploy-stack

  # Service Quotas 自動管理を有効化（通知ARNはスタック出力を自動利用）
  AWS_DEFAULT_REGION=ap-northeast-1 \
  $0 enable-auto-management
EOF
    exit 1
}

build_deploy_parameter_overrides() {
    DEPLOY_PARAMS=(
        "ServiceQuotaNotificationName=${SERVICE_QUOTA_NOTIFICATION_NAME}"
        "ServiceQuotaNotificationDescription=${SERVICE_QUOTA_NOTIFICATION_DESCRIPTION}"
        "ServiceQuotaAggregationDuration=${SERVICE_QUOTA_AGGREGATION_DURATION}"
    )
    if [ -n "${SERVICE_QUOTA_SLACK_CHANNEL_ARN}" ]; then
        DEPLOY_PARAMS+=("ServiceQuotaSlackChannelArn=${SERVICE_QUOTA_SLACK_CHANNEL_ARN}")
    fi
}

build_stackset_parameter_overrides() {
    STACKSET_PARAMS=(
        "ParameterKey=ServiceQuotaNotificationName,ParameterValue=${SERVICE_QUOTA_NOTIFICATION_NAME}"
        "ParameterKey=ServiceQuotaNotificationDescription,ParameterValue=${SERVICE_QUOTA_NOTIFICATION_DESCRIPTION}"
        "ParameterKey=ServiceQuotaAggregationDuration,ParameterValue=${SERVICE_QUOTA_AGGREGATION_DURATION}"
    )
    if [ -n "${SERVICE_QUOTA_SLACK_CHANNEL_ARN}" ]; then
        STACKSET_PARAMS+=("ParameterKey=ServiceQuotaSlackChannelArn,ParameterValue=${SERVICE_QUOTA_SLACK_CHANNEL_ARN}")
    fi
}

resolve_notification_arn() {
    if [ -n "${AUTO_MANAGEMENT_NOTIFICATION_ARN}" ]; then
        echo "${AUTO_MANAGEMENT_NOTIFICATION_ARN}"
        return
    fi

    local arn
    arn="$(aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query "Stacks[0].Outputs[?OutputKey=='ServiceQuotaNotificationConfigurationArn'].OutputValue | [0]" \
        --output text 2>/dev/null || true)"

    if [ -z "${arn}" ] || [ "${arn}" = "None" ]; then
        echo ""
        return
    fi
    echo "${arn}"
}

validate_template() {
    echo "テンプレートを検証中: ${TEMPLATE_FILE}"
    aws cloudformation validate-template \
        --template-body "file://${TEMPLATE_FILE}" \
        --region "${REGION}"
    echo "テンプレートの検証に成功しました"
}

deploy_stack() {
    echo "CloudFormation スタックをデプロイ中..."
    echo "  スタック名: ${STACK_NAME}"
    echo "  リージョン: ${REGION}"
    if [ -n "${SERVICE_QUOTA_SLACK_CHANNEL_ARN}" ]; then
        echo "  Slack通知連携: 有効"
    else
        echo "  Slack通知連携: 無効 (ServiceQuotaNotificationConfiguration のみ作成)"
    fi
    echo ""

    build_deploy_parameter_overrides

    aws cloudformation deploy \
        --template-file "${TEMPLATE_FILE}" \
        --stack-name "${STACK_NAME}" \
        --parameter-overrides "${DEPLOY_PARAMS[@]}" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "${REGION}" \
        --no-fail-on-empty-changeset

    echo ""
    echo "デプロイ完了。スタック出力:"
    aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
}

deploy_stackset() {
    echo "CloudFormation StackSet を作成中..."
    echo "  StackSet 名: ${STACKSET_NAME}"
    if [ -n "${SERVICE_QUOTA_SLACK_CHANNEL_ARN}" ]; then
        echo "  Slack通知連携: 有効"
    else
        echo "  Slack通知連携: 無効"
    fi
    echo ""

    build_stackset_parameter_overrides

    if aws cloudformation describe-stack-set --stack-set-name "${STACKSET_NAME}" --region "${REGION}" &>/dev/null; then
        echo "StackSet '${STACKSET_NAME}' は既に存在します。更新中..."
        aws cloudformation update-stack-set \
            --stack-set-name "${STACKSET_NAME}" \
            --template-body "file://${TEMPLATE_FILE}" \
            --parameter-overrides "${STACKSET_PARAMS[@]}" \
            --capabilities CAPABILITY_NAMED_IAM \
            --region "${REGION}"
    else
        echo "StackSet '${STACKSET_NAME}' を作成中..."
        aws cloudformation create-stack-set \
            --stack-set-name "${STACKSET_NAME}" \
            --template-body "file://${TEMPLATE_FILE}" \
            --parameter-overrides "${STACKSET_PARAMS[@]}" \
            --capabilities CAPABILITY_NAMED_IAM \
            --region "${REGION}"
    fi

    echo ""
    echo "StackSet の作成/更新が完了しました。"
    echo "インスタンスを追加するには: $0 add-instances"
}

add_stackset_instances() {
    local regions="${REGIONS:-${REGION}}"
    local ou_ids="${OU_IDS:-}"
    local account_ids="${ACCOUNT_IDS:-}"

    echo "StackSet インスタンスを追加中..."
    echo "  StackSet 名: ${STACKSET_NAME}"
    echo "  リージョン: ${regions}"

    REGIONS_ARG=$(echo "${regions}" | tr ',' ' ')

    if [ -n "${ou_ids}" ]; then
        echo "  対象 OU: ${ou_ids}"
        IFS=',' read -ra OU_ARRAY <<< "${ou_ids}"
        OU_JSON=$(printf '"%s",' "${OU_ARRAY[@]}" | sed 's/,$//')
        aws cloudformation create-stack-instances \
            --stack-set-name "${STACKSET_NAME}" \
            --regions ${REGIONS_ARG} \
            --deployment-targets "{\"OrganizationalUnitIds\":[${OU_JSON}]}" \
            --operation-preferences "FailureToleranceCount=0,MaxConcurrentCount=5" \
            --region "${REGION}"
    elif [ -n "${account_ids}" ]; then
        echo "  対象アカウント: ${account_ids}"
        aws cloudformation create-stack-instances \
            --stack-set-name "${STACKSET_NAME}" \
            --accounts ${account_ids//,/ } \
            --regions ${REGIONS_ARG} \
            --operation-preferences "FailureToleranceCount=0,MaxConcurrentCount=5" \
            --region "${REGION}"
    else
        echo "エラー: OU_IDS または ACCOUNT_IDS を指定してください"
        exit 1
    fi

    echo ""
    echo "StackSet インスタンスの追加を開始しました。"
}

delete_stack() {
    echo "スタックを削除中: ${STACK_NAME}"
    aws cloudformation delete-stack \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}"
    echo "削除を開始しました。進行状況: $0 status"
}

delete_stackset() {
    echo "StackSet を削除中: ${STACKSET_NAME}"
    echo "警告: まず全インスタンスを削除してください"
    aws cloudformation delete-stack-set \
        --stack-set-name "${STACKSET_NAME}" \
        --region "${REGION}"
    echo "StackSet の削除が完了しました。"
}

show_status() {
    echo "スタック '${STACK_NAME}' のステータス:"
    aws cloudformation describe-stacks \
        --stack-name "${STACK_NAME}" \
        --region "${REGION}" \
        --query 'Stacks[0].[StackName,StackStatus,LastUpdatedTime]' \
        --output table 2>/dev/null || echo "スタックが見つかりません: ${STACK_NAME}"
}

enable_auto_management() {
    local notification_arn

    notification_arn="$(resolve_notification_arn)"
    if [ -z "${notification_arn}" ]; then
        echo "エラー: 通知ARNを取得できませんでした。"
        echo "  1) deploy-stack でスタックを作成する、または"
        echo "  2) AUTO_MANAGEMENT_NOTIFICATION_ARN を指定してください。"
        exit 1
    fi

    echo "Service Quotas 自動管理を適用中..."
    echo "  リージョン: ${REGION}"
    echo "  opt-in-level: ${AUTO_MANAGEMENT_OPT_IN_LEVEL}"
    echo "  opt-in-type: ${AUTO_MANAGEMENT_OPT_IN_TYPE}"
    echo "  notification-arn: ${notification_arn}"

    if aws service-quotas get-auto-management-configuration --region "${REGION}" >/dev/null 2>&1; then
        echo "既存設定を更新します (update-auto-management)。"
        if [ -n "${AUTO_MANAGEMENT_EXCLUSION_LIST}" ]; then
            aws service-quotas update-auto-management \
                --opt-in-type "${AUTO_MANAGEMENT_OPT_IN_TYPE}" \
                --notification-arn "${notification_arn}" \
                --exclusion-list "${AUTO_MANAGEMENT_EXCLUSION_LIST}" \
                --region "${REGION}"
        else
            aws service-quotas update-auto-management \
                --opt-in-type "${AUTO_MANAGEMENT_OPT_IN_TYPE}" \
                --notification-arn "${notification_arn}" \
                --region "${REGION}"
        fi
    else
        echo "新規に有効化します (start-auto-management)。"
        if [ -n "${AUTO_MANAGEMENT_EXCLUSION_LIST}" ]; then
            aws service-quotas start-auto-management \
                --opt-in-level "${AUTO_MANAGEMENT_OPT_IN_LEVEL}" \
                --opt-in-type "${AUTO_MANAGEMENT_OPT_IN_TYPE}" \
                --notification-arn "${notification_arn}" \
                --exclusion-list "${AUTO_MANAGEMENT_EXCLUSION_LIST}" \
                --region "${REGION}"
        else
            aws service-quotas start-auto-management \
                --opt-in-level "${AUTO_MANAGEMENT_OPT_IN_LEVEL}" \
                --opt-in-type "${AUTO_MANAGEMENT_OPT_IN_TYPE}" \
                --notification-arn "${notification_arn}" \
                --region "${REGION}"
        fi
    fi

    echo ""
    show_auto_management
}

show_auto_management() {
    aws service-quotas get-auto-management-configuration \
        --region "${REGION}"
}

if [ $# -eq 0 ]; then
    usage
fi

case "$1" in
    deploy-stack)
        validate_template
        deploy_stack
        ;;
    deploy-stackset)
        validate_template
        deploy_stackset
        ;;
    add-instances)
        add_stackset_instances
        ;;
    enable-auto-management)
        enable_auto_management
        ;;
    show-auto-management)
        show_auto_management
        ;;
    delete-stack)
        delete_stack
        ;;
    delete-stackset)
        delete_stackset
        ;;
    status)
        show_status
        ;;
    validate)
        validate_template
        ;;
    *)
        echo "不明なコマンド: $1"
        usage
        ;;
esac
