#!/bin/bash
# CloudWatch Service Quota Monitoring - デプロイスクリプト

set -euo pipefail

STACK_NAME="${STACK_NAME:-service-quota-monitoring}"
STACKSET_NAME="${STACKSET_NAME:-service-quota-monitoring}"
TEMPLATE_FILE="$(dirname "$0")/../cfn/stackset-template.yaml"
REGION="${AWS_DEFAULT_REGION:-ap-northeast-1}"
THRESHOLD_PERCENT="${THRESHOLD_PERCENT:-80}"
MONITORING_SCHEDULE="${MONITORING_SCHEDULE:-rate(1 hour)}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-}"
EXISTING_TOPIC_ARN="${EXISTING_TOPIC_ARN:-}"
EC2_VCPU_QUOTA="${EC2_VCPU_QUOTA:-32}"
LAMBDA_CONCURRENCY_QUOTA="${LAMBDA_CONCURRENCY_QUOTA:-1000}"

usage() {
    cat <<EOF
使用方法:
  $0 <command> [options]

コマンド:
  deploy-stack      CloudFormation スタックとしてデプロイ（単一アカウント）
  deploy-stackset   CloudFormation StackSet としてデプロイ（複数アカウント/リージョン）
  add-instances     StackSet インスタンスを追加（deploy-stackset 実行後）
  delete-stack      スタックを削除
  delete-stackset   StackSet を削除
  status            スタックのステータスを確認
  validate          テンプレートを検証

環境変数:
  STACK_NAME              スタック名 (デフォルト: service-quota-monitoring)
  STACKSET_NAME           StackSet 名 (デフォルト: service-quota-monitoring)
  AWS_DEFAULT_REGION      デプロイ先リージョン (デフォルト: ap-northeast-1)
  THRESHOLD_PERCENT       クォータ使用率アラーム閾値 % (デフォルト: 80)
  MONITORING_SCHEDULE     監視スケジュール (デフォルト: rate(1 hour))
  NOTIFICATION_EMAIL      通知メールアドレス (任意)
  EXISTING_TOPIC_ARN      既存の SNS トピック ARN (任意)
  EC2_VCPU_QUOTA          EC2 On-Demand 標準 vCPU クォータ (デフォルト: 32)
  LAMBDA_CONCURRENCY_QUOTA Lambda 同時実行数クォータ (デフォルト: 1000)

例:
  # 単一アカウントへのデプロイ
  NOTIFICATION_EMAIL=admin@example.com $0 deploy-stack

  # StackSet の作成
  $0 deploy-stackset

  # StackSet のインスタンスを組織 OU に追加
  OU_IDS=ou-xxxx-xxxxxxxx REGIONS=ap-northeast-1,us-east-1 $0 add-instances

  # 特定アカウントに StackSet インスタンスを追加
  ACCOUNT_IDS=123456789012 REGIONS=ap-northeast-1 $0 add-instances
EOF
    exit 1
}

build_parameter_overrides() {
    local params="ParameterKey=ThresholdPercent,ParameterValue=${THRESHOLD_PERCENT}"
    params="${params} ParameterKey=MonitoringSchedule,ParameterValue=${MONITORING_SCHEDULE}"
    params="${params} ParameterKey=EC2StandardVCPUQuota,ParameterValue=${EC2_VCPU_QUOTA}"
    params="${params} ParameterKey=LambdaConcurrentExecutionsQuota,ParameterValue=${LAMBDA_CONCURRENCY_QUOTA}"
    if [ -n "${NOTIFICATION_EMAIL}" ]; then
        params="${params} ParameterKey=NotificationEmail,ParameterValue=${NOTIFICATION_EMAIL}"
    fi
    if [ -n "${EXISTING_TOPIC_ARN}" ]; then
        params="${params} ParameterKey=ExistingTopicArn,ParameterValue=${EXISTING_TOPIC_ARN}"
    fi
    echo "${params}"
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
    echo "  閾値: ${THRESHOLD_PERCENT}%"
    echo "  スケジュール: ${MONITORING_SCHEDULE}"
    echo ""

    PARAMS=$(build_parameter_overrides)

    aws cloudformation deploy \
        --template-file "${TEMPLATE_FILE}" \
        --stack-name "${STACK_NAME}" \
        --parameter-overrides ${PARAMS} \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
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
    echo "  閾値: ${THRESHOLD_PERCENT}%"
    echo "  スケジュール: ${MONITORING_SCHEDULE}"
    echo ""

    PARAMS=$(build_parameter_overrides)

    # StackSet が既に存在するか確認
    if aws cloudformation describe-stack-set --stack-set-name "${STACKSET_NAME}" --region "${REGION}" &>/dev/null; then
        echo "StackSet '${STACKSET_NAME}' は既に存在します。更新中..."
        aws cloudformation update-stack-set \
            --stack-set-name "${STACKSET_NAME}" \
            --template-body "file://${TEMPLATE_FILE}" \
            --parameter-overrides ${PARAMS} \
            --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
            --region "${REGION}"
    else
        echo "StackSet '${STACKSET_NAME}' を作成中..."
        aws cloudformation create-stack-set \
            --stack-set-name "${STACKSET_NAME}" \
            --template-body "file://${TEMPLATE_FILE}" \
            --parameter-overrides ${PARAMS} \
            --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
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
        # Convert comma-separated OU IDs to JSON array
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

# メイン処理
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
