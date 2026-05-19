#!/bin/bash
# Trusted Advisor refresh workflow + Slack notification deployment script

set -euo pipefail

STACK_NAME="${STACK_NAME:-service-quota-monitoring}"
STACKSET_NAME="${STACKSET_NAME:-service-quota-monitoring}"
TEMPLATE_FILE="$(dirname "$0")/../cfn/stackset-template.yaml"
REGION="${AWS_DEFAULT_REGION:-ap-northeast-1}"
TRUSTED_ADVISOR_REFRESH_SCHEDULE="${TRUSTED_ADVISOR_REFRESH_SCHEDULE:-rate(6 hours)}"
TRUSTED_ADVISOR_CHECK_IDS="${TRUSTED_ADVISOR_CHECK_IDS:-}"
TRUSTED_ADVISOR_DEFINITION_FILE="${TRUSTED_ADVISOR_DEFINITION_FILE:-$(dirname "$0")/../asl/trusted-advisor-refresh.asl.json}"
TRUSTED_ADVISOR_DEFINITION_S3_BUCKET="${TRUSTED_ADVISOR_DEFINITION_S3_BUCKET:-}"
TRUSTED_ADVISOR_DEFINITION_S3_KEY="${TRUSTED_ADVISOR_DEFINITION_S3_KEY:-}"
TRUSTED_ADVISOR_SLACK_CHANNEL_ARN="${TRUSTED_ADVISOR_SLACK_CHANNEL_ARN:-}"
TRUSTED_ADVISOR_NOTIFICATION_REGIONS="${TRUSTED_ADVISOR_NOTIFICATION_REGIONS:-us-east-1,us-east-2,us-west-2,eu-west-1,eu-central-1,ap-northeast-1,ap-southeast-1,ap-southeast-2,ap-south-1,ca-central-1,sa-east-1}"

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
  STACK_NAME                          スタック名 (デフォルト: service-quota-monitoring)
  STACKSET_NAME                       StackSet 名 (デフォルト: service-quota-monitoring)
  AWS_DEFAULT_REGION                  デプロイ先リージョン (デフォルト: ap-northeast-1)
  TRUSTED_ADVISOR_REFRESH_SCHEDULE    TAリフレッシュの定期実行式 (デフォルト: rate(6 hours))
  TRUSTED_ADVISOR_CHECK_IDS           リフレッシュ対象のTAチェックID(カンマ区切り, 任意)
  TRUSTED_ADVISOR_DEFINITION_FILE     ステートマシン定義ASLファイル
  TRUSTED_ADVISOR_DEFINITION_S3_BUCKET ASLファイルを保存するS3バケット
  TRUSTED_ADVISOR_DEFINITION_S3_KEY   ASLファイルのS3キー(任意)
  TRUSTED_ADVISOR_SLACK_CHANNEL_ARN   AWS User Notificationsで通知先にするSlackチャネルARN(任意)
    TRUSTED_ADVISOR_NOTIFICATION_REGIONS AWS User Notifications EventRuleの対象リージョン(カンマ区切り)

例:
  # 単一アカウントへのデプロイ
  $0 deploy-stack

  # TAチェックを6時間ごとにリフレッシュしSlack通知（us-east-1でのみ有効）
  AWS_DEFAULT_REGION=us-east-1 \
  TRUSTED_ADVISOR_CHECK_IDS=eW7HH0l7J9,c1z7kmr03n \
  TRUSTED_ADVISOR_DEFINITION_S3_BUCKET=my-cfn-artifacts-bucket \
  TRUSTED_ADVISOR_SLACK_CHANNEL_ARN=arn:aws:chatbot:us-east-1:123456789012:chat-configuration/slack-channel/my-channel \
    TRUSTED_ADVISOR_NOTIFICATION_REGIONS=us-east-1,ap-northeast-1,eu-west-1 \
  TRUSTED_ADVISOR_REFRESH_SCHEDULE='rate(6 hours)' \
  $0 deploy-stack
EOF
    exit 1
}

upload_trusted_advisor_definition_if_needed() {
    if [ -z "${TRUSTED_ADVISOR_CHECK_IDS}" ]; then
        return
    fi

    if [ -z "${TRUSTED_ADVISOR_DEFINITION_S3_BUCKET}" ]; then
        echo "エラー: TRUSTED_ADVISOR_CHECK_IDS を指定した場合は TRUSTED_ADVISOR_DEFINITION_S3_BUCKET が必須です"
        exit 1
    fi

    if [ ! -f "${TRUSTED_ADVISOR_DEFINITION_FILE}" ]; then
        echo "エラー: ステートマシン定義ファイルが見つかりません: ${TRUSTED_ADVISOR_DEFINITION_FILE}"
        exit 1
    fi

    if [ -z "${TRUSTED_ADVISOR_DEFINITION_S3_KEY}" ]; then
        TRUSTED_ADVISOR_DEFINITION_S3_KEY="state-machines/${STACK_NAME}/trusted-advisor-refresh.asl.json"
    fi

    echo "ステートマシン定義をS3へアップロード中..."
    aws s3 cp \
        "${TRUSTED_ADVISOR_DEFINITION_FILE}" \
        "s3://${TRUSTED_ADVISOR_DEFINITION_S3_BUCKET}/${TRUSTED_ADVISOR_DEFINITION_S3_KEY}" \
        --region "${REGION}"
}

build_deploy_parameter_overrides() {
    DEPLOY_PARAMS=(
        "TrustedAdvisorRefreshSchedule=${TRUSTED_ADVISOR_REFRESH_SCHEDULE}"
        "TrustedAdvisorNotificationRegions=${TRUSTED_ADVISOR_NOTIFICATION_REGIONS}"
    )
    if [ -n "${TRUSTED_ADVISOR_CHECK_IDS}" ]; then
        DEPLOY_PARAMS+=("TrustedAdvisorCheckIds=${TRUSTED_ADVISOR_CHECK_IDS}")
        DEPLOY_PARAMS+=("TrustedAdvisorDefinitionS3Bucket=${TRUSTED_ADVISOR_DEFINITION_S3_BUCKET}")
        DEPLOY_PARAMS+=("TrustedAdvisorDefinitionS3Key=${TRUSTED_ADVISOR_DEFINITION_S3_KEY}")
    fi
    if [ -n "${TRUSTED_ADVISOR_SLACK_CHANNEL_ARN}" ]; then
        DEPLOY_PARAMS+=("TrustedAdvisorSlackChannelArn=${TRUSTED_ADVISOR_SLACK_CHANNEL_ARN}")
    fi
}

build_stackset_parameter_overrides() {
    STACKSET_PARAMS=(
        "ParameterKey=TrustedAdvisorRefreshSchedule,ParameterValue=${TRUSTED_ADVISOR_REFRESH_SCHEDULE}"
        "ParameterKey=TrustedAdvisorNotificationRegions,ParameterValue=${TRUSTED_ADVISOR_NOTIFICATION_REGIONS}"
    )
    if [ -n "${TRUSTED_ADVISOR_CHECK_IDS}" ]; then
        STACKSET_PARAMS+=("ParameterKey=TrustedAdvisorCheckIds,ParameterValue=${TRUSTED_ADVISOR_CHECK_IDS}")
        STACKSET_PARAMS+=("ParameterKey=TrustedAdvisorDefinitionS3Bucket,ParameterValue=${TRUSTED_ADVISOR_DEFINITION_S3_BUCKET}")
        STACKSET_PARAMS+=("ParameterKey=TrustedAdvisorDefinitionS3Key,ParameterValue=${TRUSTED_ADVISOR_DEFINITION_S3_KEY}")
    fi
    if [ -n "${TRUSTED_ADVISOR_SLACK_CHANNEL_ARN}" ]; then
        STACKSET_PARAMS+=("ParameterKey=TrustedAdvisorSlackChannelArn,ParameterValue=${TRUSTED_ADVISOR_SLACK_CHANNEL_ARN}")
    fi
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
    if [ -n "${TRUSTED_ADVISOR_CHECK_IDS}" ]; then
        echo "  TA定期リフレッシュ: 有効"
    else
        echo "  TA定期リフレッシュ: 無効 (TRUSTED_ADVISOR_CHECK_IDS未指定)"
    fi
    if [ -n "${TRUSTED_ADVISOR_SLACK_CHANNEL_ARN}" ]; then
        echo "  TAリフレッシュ通知(User Notifications->Slack): 有効"
    else
        echo "  TAリフレッシュ通知(User Notifications->Slack): 無効"
    fi
    echo ""

    upload_trusted_advisor_definition_if_needed
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
    if [ -n "${TRUSTED_ADVISOR_CHECK_IDS}" ]; then
        echo "  TA定期リフレッシュ: 有効 (us-east-1でのみ作成)"
    else
        echo "  TA定期リフレッシュ: 無効"
    fi
    if [ -n "${TRUSTED_ADVISOR_SLACK_CHANNEL_ARN}" ]; then
        echo "  TAリフレッシュ通知(User Notifications->Slack): 有効 (us-east-1でのみ作成)"
    else
        echo "  TAリフレッシュ通知(User Notifications->Slack): 無効"
    fi
    echo ""

    upload_trusted_advisor_definition_if_needed
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
