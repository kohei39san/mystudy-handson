#!/bin/bash

# Tag Policy Owner Tag Enforcement - デプロイスクリプト

STACK_NAME="tag-policy-owner-enforcement"
TEMPLATE_FILE="../cfn/tag-policy-template.yaml"
POLICY_NAME="OwnerTagPolicy"
POLICY_DESCRIPTION="Enforce Owner tag with specific value pattern"
DEFAULT_OWNER_VALUE="*@example.com"

# パラメータの確認
if [ $# -eq 0 ]; then
    echo "使用方法:"
    echo "  $0 deploy                          # Tag Policyを作成（アタッチなし）"
    echo "  $0 deploy <OU-ID or Account-ID>    # Tag Policyを作成して指定のターゲットにアタッチ"
    echo "  $0 deploy <OU-ID> <owner-value>    # カスタムOwner値でTag Policyを作成"
    echo "  $0 delete                          # スタックを削除"
    echo "  $0 status                          # スタックの状態を確認"
    echo ""
    echo "例:"
    echo "  $0 deploy ou-xxxx-xxxxxxxx *@example.com"
    echo "  $0 deploy ou-xxxx-xxxxxxxx UserName*"
    exit 1
fi

case "$1" in
    deploy)
        if [ -z "$2" ]; then
            # ターゲットIDが指定されていない場合
            echo "Tag Policyを作成中..."
            aws cloudformation create-stack \
                --stack-name ${STACK_NAME} \
                --template-body file://${TEMPLATE_FILE} \
                --parameters file://../src/tag-policy-parameters.json
        else
            # ターゲットIDが指定されている場合
            OWNER_VALUE=${3:-${DEFAULT_OWNER_VALUE}}
            echo "Tag Policyを作成し、${2} にアタッチ中... (Owner Value: ${OWNER_VALUE})"
            aws cloudformation create-stack \
                --stack-name ${STACK_NAME} \
                --template-body file://${TEMPLATE_FILE} \
                --parameters \
                    ParameterKey=PolicyName,ParameterValue=${POLICY_NAME} \
                    ParameterKey=PolicyDescription,ParameterValue="${POLICY_DESCRIPTION}" \
                    ParameterKey=AllowedOwnerValue,ParameterValue="${OWNER_VALUE}" \
                    ParameterKey=TargetIds,ParameterValue="${2}"
        fi
        
        if [ $? -eq 0 ]; then
            echo "デプロイを開始しました。"
            echo "進行状況を確認するには: $0 status"
        fi
        ;;
        
    delete)
        echo "スタックを削除中..."
        aws cloudformation delete-stack --stack-name ${STACK_NAME}
        
        if [ $? -eq 0 ]; then
            echo "削除を開始しました。"
            echo "進行状況を確認するには: $0 status"
        fi
        ;;
        
    status)
        aws cloudformation describe-stacks \
            --stack-name ${STACK_NAME} \
            --query 'Stacks[0].[StackName,StackStatus]' \
            --output table
        ;;
        
    *)
        echo "不明なコマンド: $1"
        echo "使用可能なコマンド: deploy, delete, status"
        exit 1
        ;;
esac