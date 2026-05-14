#!/bin/bash
# Deploy Azure budget alert using ARM template via subscription-level deployment
# Usage: ./deploy.sh [options]
#
# Prerequisites:
#   - Azure CLI installed and logged in (az login)
#   - Subscription ID set via AZURE_SUBSCRIPTION_ID environment variable or --subscription-id flag

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE_FILE="$PROJECT_DIR/cfn/budget.json"

# Default values
DEPLOYMENT_NAME="billing-alert-deployment"
LOCATION="japaneast"
BUDGET_NAME="Monthly-Billing-Alert"
BUDGET_AMOUNT=100
TIME_GRAIN="Monthly"
CONTACT_ROLES='["Owner"]'
ACTUAL_THRESHOLD_1=50
ACTUAL_THRESHOLD_2=80
ACTUAL_THRESHOLD_3=100
FORECASTED_THRESHOLD=100

usage() {
  cat <<EOF
Usage: $0 [options]

Options:
  --subscription-id   SUBSCRIPTION_ID   Azure subscription ID (or set AZURE_SUBSCRIPTION_ID env var)
  --location          LOCATION          Azure region for deployment (default: japaneast)
  --deployment-name   NAME              Deployment name (default: billing-alert-deployment)
  --budget-name       NAME              Budget name (default: Monthly-Billing-Alert)
  --budget-amount     AMOUNT            Budget amount (default: 100)
  --time-grain        GRAIN             Time grain: Monthly|Quarterly|Annual (default: Monthly)
  --start-date        DATE              Budget start date YYYY-MM-DD (must be first of month)
  --end-date          DATE              Budget end date YYYY-MM-DD
  --contact-emails    EMAILS            JSON array of email addresses e.g. '["a@b.com","c@d.com"]'
  --contact-roles     ROLES             JSON array of roles e.g. '["Owner"]' (default: ["Owner"])
  --threshold1        PERCENT           First actual alert threshold % (default: 50)
  --threshold2        PERCENT           Second actual alert threshold % (default: 80)
  --threshold3        PERCENT           Third actual alert threshold % (default: 100)
  --forecasted        PERCENT           Forecasted alert threshold % (default: 100)
  --destroy                             Delete the budget deployment
  -h, --help                            Show this help message

Examples:
  # Deploy with required parameters
  $0 \\
    --subscription-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \\
    --start-date "2025-01-01" \\
    --end-date "2025-12-31" \\
    --contact-emails '["admin@example.com","finance@example.com"]'

  # Destroy the deployment
  $0 --subscription-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" --destroy
EOF
}

DESTROY=false
SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID:-}"
START_DATE=""
END_DATE=""
CONTACT_EMAILS=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --subscription-id)   SUBSCRIPTION_ID="$2"; shift 2 ;;
    --location)          LOCATION="$2"; shift 2 ;;
    --deployment-name)   DEPLOYMENT_NAME="$2"; shift 2 ;;
    --budget-name)       BUDGET_NAME="$2"; shift 2 ;;
    --budget-amount)     BUDGET_AMOUNT="$2"; shift 2 ;;
    --time-grain)        TIME_GRAIN="$2"; shift 2 ;;
    --start-date)        START_DATE="$2"; shift 2 ;;
    --end-date)          END_DATE="$2"; shift 2 ;;
    --contact-emails)    CONTACT_EMAILS="$2"; shift 2 ;;
    --contact-roles)     CONTACT_ROLES="$2"; shift 2 ;;
    --threshold1)        ACTUAL_THRESHOLD_1="$2"; shift 2 ;;
    --threshold2)        ACTUAL_THRESHOLD_2="$2"; shift 2 ;;
    --threshold3)        ACTUAL_THRESHOLD_3="$2"; shift 2 ;;
    --forecasted)        FORECASTED_THRESHOLD="$2"; shift 2 ;;
    --destroy)           DESTROY=true; shift ;;
    -h|--help)           usage; exit 0 ;;
    *)                   echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

if [[ -z "$SUBSCRIPTION_ID" ]]; then
  echo "Error: --subscription-id or AZURE_SUBSCRIPTION_ID environment variable is required."
  usage
  exit 1
fi

echo "Setting Azure subscription to: $SUBSCRIPTION_ID"
az account set --subscription "$SUBSCRIPTION_ID"

if [[ "$DESTROY" == "true" ]]; then
  echo "Deleting budget: $BUDGET_NAME"
  az consumption budget delete \
    --budget-name "$BUDGET_NAME" \
    --subscription "$SUBSCRIPTION_ID" || echo "Budget not found or already deleted."
  echo "Done."
  exit 0
fi

if [[ -z "$START_DATE" || -z "$END_DATE" || -z "$CONTACT_EMAILS" ]]; then
  echo "Error: --start-date, --end-date, and --contact-emails are required."
  usage
  exit 1
fi

echo "Deploying Azure budget alert via ARM template..."
echo "  Subscription:  $SUBSCRIPTION_ID"
echo "  Location:      $LOCATION"
echo "  Budget name:   $BUDGET_NAME"
echo "  Budget amount: $BUDGET_AMOUNT"
echo "  Time grain:    $TIME_GRAIN"
echo "  Start date:    $START_DATE"
echo "  End date:      $END_DATE"
echo ""

az deployment sub create \
  --name "$DEPLOYMENT_NAME" \
  --location "$LOCATION" \
  --template-file "$TEMPLATE_FILE" \
  --parameters \
    budgetName="$BUDGET_NAME" \
    amount="$BUDGET_AMOUNT" \
    timeGrain="$TIME_GRAIN" \
    startDate="$START_DATE" \
    endDate="$END_DATE" \
    contactEmails="$CONTACT_EMAILS" \
    contactRoles="$CONTACT_ROLES" \
    actualAlertThreshold1="$ACTUAL_THRESHOLD_1" \
    actualAlertThreshold2="$ACTUAL_THRESHOLD_2" \
    actualAlertThreshold3="$ACTUAL_THRESHOLD_3" \
    forecastedAlertThreshold="$FORECASTED_THRESHOLD"

echo ""
echo "Deployment completed successfully."
echo "View your budget at: https://portal.azure.com/#view/Microsoft_Azure_CostManagement/BudgetList"
