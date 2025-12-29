#!/bin/bash

# SCP Owner Tag Enforcement - デプロイスクリプト

STACK_NAME="scp-owner-tag-enforcement"
TEMPLATE_FILE="../cfn/scp-template.yaml"
POLICY_NAME="EnforceOwnerTagPolicy"
POLICY_DESCRIPTION="Deny resource creation without Owner tag"

# パラメータの確認
if [ $# -eq 0 ]; then
    echo "使用方法:"
    echo "  $0 deploy                          # ポリシーを作成（アタッチなし）"
    echo "  $0 deploy <OU-ID or Account-ID>    # ポリシーを作成して指定のターゲットにアタッチ"
    echo "  $0 delete                          # スタックを削除"
    echo "  $0 status                          # スタックの状態を確認"
    exit 1
fi

case "$1" in
    deploy)
        if [ -z "$2" ]; then
            # ターゲットIDが指定されていない場合
            echo "SCPポリシーを作成中..."
            aws cloudformation create-stack \
                --stack-name ${STACK_NAME} \
                --template-body file://${TEMPLATE_FILE} \
                --parameters file://../src/scp-parameters.json
        else
            # ターゲットIDが指定されている場合
            echo "SCPポリシーを作成し、${2} にアタッチ中..."
            aws cloudformation create-stack \
                --stack-name ${STACK_NAME} \
                --template-body file://${TEMPLATE_FILE} \
                --parameters \
                    ParameterKey=PolicyName,ParameterValue=${POLICY_NAME} \
                    ParameterKey=PolicyDescription,ParameterValue="${POLICY_DESCRIPTION}" \
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