#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./tests/stepfunctions/run-local-tests.sh
#
# Optional environment variables:
#   ENDPOINT_URL (default: http://localhost:8083)
#   STATE_MACHINE_NAME (default: ta-refresh-local)
#   ROLE_ARN (default: arn:aws:iam::012345678901:role/DummyRole)
#   INPUT_FILE (default: tests/fixtures/trusted-advisor-refresh-input.json)
#
# If you want mocked integrations, start Step Functions Local with MockConfigFile.json mounted.
# Example:
#   docker run --rm -p 8083:8083 \
#     -v "$PWD/tests/stepfunctions/MockConfigFile.json:/home/stepfunctionslocal/MockConfigFile.json" \
#     -e SFN_MOCK_CONFIG=/home/stepfunctionslocal/MockConfigFile.json \
#     amazon/aws-stepfunctions-local

ENDPOINT_URL="${ENDPOINT_URL:-http://localhost:8083}"
STATE_MACHINE_NAME="${STATE_MACHINE_NAME:-ta-refresh-local}"
ROLE_ARN="${ROLE_ARN:-arn:aws:iam::012345678901:role/DummyRole}"
INPUT_FILE="${INPUT_FILE:-tests/fixtures/trusted-advisor-refresh-input.json}"
DEFINITION_FILE="asl/trusted-advisor-refresh.asl.json"

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI is required" >&2
  exit 1
fi

if [[ ! -f "$DEFINITION_FILE" ]]; then
  echo "Definition file not found: $DEFINITION_FILE" >&2
  exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Input file not found: $INPUT_FILE" >&2
  exit 1
fi

ACCOUNT_ID="012345678901"
REGION="us-east-1"
STATE_MACHINE_ARN="arn:aws:states:${REGION}:${ACCOUNT_ID}:stateMachine:${STATE_MACHINE_NAME}"

echo "Deleting old state machine if exists..."
aws stepfunctions delete-state-machine \
  --endpoint-url "$ENDPOINT_URL" \
  --state-machine-arn "$STATE_MACHINE_ARN" >/dev/null 2>&1 || true

echo "Creating state machine..."
aws stepfunctions create-state-machine \
  --endpoint-url "$ENDPOINT_URL" \
  --name "$STATE_MACHINE_NAME" \
  --definition "file://$DEFINITION_FILE" \
  --role-arn "$ROLE_ARN" >/dev/null

echo "Starting execution..."
EXECUTION_ARN="$(aws stepfunctions start-execution \
  --endpoint-url "$ENDPOINT_URL" \
  --state-machine-arn "$STATE_MACHINE_ARN" \
  --input "$(cat "$INPUT_FILE")" \
  --query executionArn \
  --output text)"

echo "Execution ARN: $EXECUTION_ARN"

echo "Execution history:"
aws stepfunctions get-execution-history \
  --endpoint-url "$ENDPOINT_URL" \
  --execution-arn "$EXECUTION_ARN" \
  --max-items 200

echo "Done"
