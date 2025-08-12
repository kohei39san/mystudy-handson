#!/bin/bash
# Cleanup script for OCI Cost Alert resources

set -e

echo "=== OCI Cost Alert Cleanup ==="
echo "This script will destroy all resources created by this Terraform configuration."
echo ""

# Confirm destruction
read -p "Are you sure you want to destroy all resources? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "🗑️  Destroying resources..."

# Run terraform destroy
terraform destroy -auto-approve

if [ $? -eq 0 ]; then
    echo "✅ All resources have been successfully destroyed"
    echo ""
    echo "Note: You may need to manually unsubscribe from any email notifications"
    echo "if you no longer want to receive them."
else
    echo "❌ Failed to destroy some resources"
    echo "Please check the Terraform state and manually clean up if necessary"
    exit 1
fi