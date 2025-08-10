#!/bin/bash

# Destruction script for OCI Cost Alert Terraform configuration
# This script helps safely destroy the OCI budget alert infrastructure

set -e

echo "=== OCI Cost Alert Destruction Script ==="

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

# Check if Terraform state exists
if [[ ! -f "terraform.tfstate" ]] && [[ ! -f ".terraform/terraform.tfstate" ]]; then
    print_warning "No Terraform state found. Nothing to destroy."
    exit 0
fi

print_status "Found Terraform state file"

# Show current resources
print_status "Current resources managed by Terraform:"
terraform show -no-color | head -20

echo ""
print_warning "⚠️  WARNING: This will destroy all OCI budget alert resources!"
print_warning "This includes:"
echo "  - Budget configuration"
echo "  - Budget alert rules"
echo "  - Notification topics"
echo "  - Email subscriptions"
echo ""
print_warning "This action cannot be undone!"

echo ""
read -p "Are you sure you want to destroy all resources? Type 'yes' to confirm: " confirm

if [[ $confirm != "yes" ]]; then
    print_status "Destruction cancelled by user"
    exit 0
fi

echo ""
print_status "Starting Terraform destruction..."

# Terraform destroy with plan
print_status "Step 1: Terraform Destroy Plan"
if terraform plan -destroy -out=destroy.tfplan; then
    print_status "Terraform destroy plan completed"
else
    print_error "Terraform destroy plan failed"
    exit 1
fi

echo ""
print_warning "Review the destruction plan above carefully."
read -p "Proceed with destruction? Type 'yes' to confirm: " final_confirm

if [[ $final_confirm != "yes" ]]; then
    print_status "Destruction cancelled by user"
    rm -f destroy.tfplan
    exit 0
fi

echo ""
print_status "Step 2: Terraform Destroy Apply"
if terraform apply destroy.tfplan; then
    print_status "Terraform destroy completed successfully"
    rm -f destroy.tfplan
else
    print_error "Terraform destroy failed"
    rm -f destroy.tfplan
    exit 1
fi

echo ""
print_status "=== Destruction Completed Successfully! ==="
echo ""
print_status "All OCI budget alert resources have been destroyed."
print_status "You may want to clean up the Terraform state files:"
echo "  rm -f terraform.tfstate*"
echo "  rm -rf .terraform/"