#!/bin/bash

# Deployment script for OCI Cost Alert Terraform configuration
# This script helps deploy the OCI budget alert infrastructure

set -e

echo "=== OCI Cost Alert Deployment Script ==="

# Change to the directory containing the Terraform files
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if terraform.tfvars exists
if [[ ! -f "terraform.tfvars" ]]; then
    print_error "terraform.tfvars file not found!"
    print_status "Please copy terraform.tfvars.example to terraform.tfvars and update the values:"
    echo "  cp terraform.tfvars.example terraform.tfvars"
    echo "  # Edit terraform.tfvars with your specific values"
    exit 1
fi

print_status "Found terraform.tfvars file"

# Check if OCI CLI is configured
if ! command -v oci &> /dev/null; then
    print_warning "OCI CLI not found. Please install and configure OCI CLI first."
    print_status "Installation guide: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm"
fi

# Validate required variables in terraform.tfvars
print_status "Validating terraform.tfvars..."

if ! grep -q "compartment_id" terraform.tfvars; then
    print_error "compartment_id is not set in terraform.tfvars"
    exit 1
fi

if ! grep -q "alert_email_addresses" terraform.tfvars; then
    print_error "alert_email_addresses is not set in terraform.tfvars"
    exit 1
fi

print_status "terraform.tfvars validation passed"

# Run the validation test
print_status "Running validation tests..."
if bash test_validation.sh; then
    print_status "Validation tests passed"
else
    print_error "Validation tests failed"
    exit 1
fi

# Terraform deployment steps
print_status "Starting Terraform deployment..."

echo ""
print_status "Step 1: Terraform Init"
if terraform init; then
    print_status "Terraform initialization completed"
else
    print_error "Terraform initialization failed"
    exit 1
fi

echo ""
print_status "Step 2: Terraform Plan"
if terraform plan -out=tfplan; then
    print_status "Terraform plan completed successfully"
else
    print_error "Terraform plan failed"
    exit 1
fi

echo ""
print_warning "Review the plan above carefully before proceeding."
read -p "Do you want to apply these changes? (yes/no): " confirm

if [[ $confirm != "yes" ]]; then
    print_status "Deployment cancelled by user"
    rm -f tfplan
    exit 0
fi

echo ""
print_status "Step 3: Terraform Apply"
if terraform apply tfplan; then
    print_status "Terraform apply completed successfully"
    rm -f tfplan
else
    print_error "Terraform apply failed"
    rm -f tfplan
    exit 1
fi

echo ""
print_status "=== Deployment Completed Successfully! ==="
echo ""
print_status "Next steps:"
echo "1. Check your email for subscription confirmation messages"
echo "2. Click the confirmation links in the emails to activate notifications"
echo "3. Verify the budget and alert rules in the OCI Console"
echo ""
print_status "You can view the created resources with:"
echo "  terraform output"
echo ""
print_status "To destroy the resources later, run:"
echo "  terraform destroy"