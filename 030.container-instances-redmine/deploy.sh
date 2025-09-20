#!/bin/bash

# OCI Redmine Deployment Script
# This script helps deploy the Redmine infrastructure on OCI

set -e

echo "=== OCI Redmine Deployment Script ==="
echo ""

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "❌ terraform.tfvars file not found!"
    echo "Please copy terraform.tfvars.example to terraform.tfvars and configure the variables."
    echo ""
    echo "cp terraform.tfvars.example terraform.tfvars"
    echo "# Edit terraform.tfvars with your values"
    exit 1
fi

# Check if OCI CLI is configured
if ! oci iam region list >/dev/null 2>&1; then
    echo "❌ OCI CLI is not configured!"
    echo "Please run 'oci setup config' to configure OCI CLI."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Validate configuration
echo "🔍 Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "📋 Creating deployment plan..."
terraform plan -out=tfplan

# Ask for confirmation
echo ""
read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Deploying Redmine infrastructure..."
    terraform apply tfplan
    
    echo ""
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "📋 Important information:"
    echo "- Load Balancer IP: $(terraform output -raw load_balancer_ip)"
    echo "- Redmine URL: $(terraform output -raw redmine_url)"
    echo ""
    echo "⏳ Please wait 5-10 minutes for the Redmine application to fully start."
    echo "🔗 You can then access Redmine at the URL shown above."
    
    # Clean up plan file
    rm -f tfplan
else
    echo "❌ Deployment cancelled."
    rm -f tfplan
    exit 1
fi