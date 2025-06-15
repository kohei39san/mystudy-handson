#!/bin/bash

# エラーが発生したら終了
set -e

# 作業ディレクトリを設定
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="${SCRIPT_DIR}/.."
SRC_DIR="${PROJECT_DIR}/src"
JS_DIR="${SCRIPT_DIR}/js"
PY_DIR="${SCRIPT_DIR}/py"

# 必要なディレクトリが存在することを確認
mkdir -p "${PROJECT_DIR}"
mkdir -p "${SRC_DIR}"
mkdir -p "${SRC_DIR}/docker"

echo "Deploying Slack Lambda MCP Server..."

# Terraformを実行
cd "${PROJECT_DIR}"
echo "Initializing Terraform..."
terraform init

echo "Applying Terraform configuration..."
terraform apply -auto-approve

echo "Deployment completed successfully!"
echo "Next steps:"
echo "1. Create a Slack app using the manifest file at ${PROJECT_DIR}/src/slack-app.json"
echo "2. Set up the required parameters in AWS Systems Manager Parameter Store:"
echo "   - /slack-bot/token"
echo "   - /slack-bot/signing-secret"
echo "   - /slack-bot/app-token"
echo "   - /openrouter/api-key"
echo "3. Configure your GitHub repository URL and credentials in the parameter store"
echo "   - /github/repo-url"
echo "   - /github/username"
echo "   - /github/token"