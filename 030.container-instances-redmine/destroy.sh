#!/bin/bash

# OCI Redmine Destruction Script
# This script helps destroy the Redmine infrastructure on OCI

set -e

echo "=== OCI Redmine Destruction Script ==="
echo ""

# Check if terraform state exists
if [ ! -f "terraform.tfstate" ]; then
    echo "❌ No Terraform state found!"
    echo "Nothing to destroy."
    exit 1
fi

echo "⚠️  WARNING: This will destroy ALL resources created by this Terraform configuration!"
echo "This includes:"
echo "- Container Instance (Redmine application)"
echo "- MySQL HeatWave database (ALL DATA WILL BE LOST)"
echo "- Network Load Balancer"
echo "- VCN and all networking components"
echo ""

read -p "Are you sure you want to destroy all resources? Type 'yes' to confirm: " -r
echo ""

if [[ $REPLY == "yes" ]]; then
    echo "🔥 Destroying Redmine infrastructure..."
    terraform destroy -auto-approve
    
    echo ""
    echo "✅ All resources have been destroyed successfully!"
    echo ""
    echo "📋 Cleanup completed:"
    echo "- All OCI resources have been removed"
    echo "- Terraform state has been updated"
    echo ""
    echo "💡 Note: Local Terraform files (.tfstate, .terraform/) are preserved"
    echo "   You can safely delete this directory if no longer needed"
else
    echo "❌ Destruction cancelled."
    exit 1
fi