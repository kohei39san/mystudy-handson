#!/bin/bash

# Deployment script for API Gateway + Cognito + Lambda payload verification system
# This script automates the deployment process using Terraform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install Terraform first."
        exit 1
    fi
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "All prerequisites are met!"
}

# Function to get user input for configuration
get_configuration() {
    print_status "Gathering configuration..."
    
    # Get user email
    read -p "Enter email address for Cognito user [test@example.com]: " USER_EMAIL
    USER_EMAIL=${USER_EMAIL:-test@example.com}
    
    # Get allowed IP addresses
    print_warning "Current IP address restriction is set to 0.0.0.0/0 (allow all)."
    print_warning "For security, you should restrict this to specific IP addresses."
    read -p "Enter allowed IP addresses (comma-separated) [0.0.0.0/0]: " ALLOWED_IPS
    ALLOWED_IPS=${ALLOWED_IPS:-0.0.0.0/0}
    
    # Get environment
    read -p "Enter environment name [dev]: " ENVIRONMENT
    ENVIRONMENT=${ENVIRONMENT:-dev}
    
    # Create terraform.tfvars file
    cat > terraform.tfvars << EOF
environment = "$ENVIRONMENT"
user_email = "$USER_EMAIL"
allowed_ip_addresses = [$(echo "$ALLOWED_IPS" | sed 's/,/","/g' | sed 's/^/"/' | sed 's/$/"/')"]
EOF
    
    print_success "Configuration saved to terraform.tfvars"
}

# Function to deploy infrastructure
deploy_infrastructure() {
    print_status "Deploying infrastructure with Terraform..."
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    print_status "Creating deployment plan..."
    terraform plan -var-file=terraform.tfvars
    
    # Ask for confirmation
    echo
    read -p "Do you want to proceed with the deployment? (y/N): " CONFIRM
    if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled by user."
        exit 0
    fi
    
    # Apply deployment
    print_status "Applying deployment..."
    terraform apply -var-file=terraform.tfvars -auto-approve
    
    print_success "Infrastructure deployed successfully!"
}

# Function to set user password
set_user_password() {
    print_status "Setting up Cognito user password..."
    
    # Get outputs from Terraform
    USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
    USER_EMAIL=$(terraform output -raw deployment_info | jq -r '.user_email')
    
    # Generate a temporary password
    TEMP_PASSWORD="TempPass123!"
    
    print_status "Setting temporary password for user: $USER_EMAIL"
    
    # Set user password
    aws cognito-idp admin-set-user-password \
        --user-pool-id "$USER_POOL_ID" \
        --username "$USER_EMAIL" \
        --password "$TEMP_PASSWORD" \
        --permanent \
        --region ap-northeast-1
    
    print_success "User password set successfully!"
    print_warning "Temporary password: $TEMP_PASSWORD"
    print_warning "Please change this password after first login."
}

# Function to display deployment information
show_deployment_info() {
    print_status "Deployment Information:"
    echo
    
    # Get outputs from Terraform
    USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
    CLIENT_ID=$(terraform output -raw cognito_user_pool_client_id)
    API_URL=$(terraform output -raw api_gateway_url)
    USER_EMAIL=$(terraform output -raw deployment_info | jq -r '.user_email')
    
    echo "🔐 Cognito User Pool ID: $USER_POOL_ID"
    echo "📱 Client ID: $CLIENT_ID"
    echo "🌐 API Gateway URL: $API_URL"
    echo "👤 User Email: $USER_EMAIL"
    echo "🔑 Temporary Password: TempPass123!"
    echo
    
    print_status "Next Steps:"
    echo "1. Test authentication with the Cognito User Pool"
    echo "2. Use the test script to verify API functionality:"
    echo "   python test-api.py --user-pool-id $USER_POOL_ID --client-id $CLIENT_ID --api-url $API_URL --username $USER_EMAIL --password TempPass123!"
    echo "3. Check CloudWatch Logs for Lambda function output"
    echo "4. Change the temporary password for security"
    echo
    
    print_success "Deployment completed successfully!"
}

# Function to run tests
run_tests() {
    print_status "Running API tests..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_warning "Python3 is not available. Skipping automated tests."
        return
    fi
    
    # Install required Python packages
    pip3 install requests boto3 > /dev/null 2>&1 || {
        print_warning "Could not install required Python packages. Skipping automated tests."
        return
    }
    
    # Get outputs from Terraform
    USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
    CLIENT_ID=$(terraform output -raw cognito_user_pool_client_id)
    API_URL=$(terraform output -raw api_gateway_url)
    USER_EMAIL=$(terraform output -raw deployment_info | jq -r '.user_email')
    
    # Run tests
    python3 test-api.py \
        --user-pool-id "$USER_POOL_ID" \
        --client-id "$CLIENT_ID" \
        --api-url "$API_URL" \
        --username "$USER_EMAIL" \
        --password "TempPass123!" || {
        print_warning "Some tests failed. Check the output above for details."
    }
}

# Main deployment flow
main() {
    echo "🚀 API Gateway + Cognito + Lambda Deployment Script"
    echo "=================================================="
    echo
    
    check_prerequisites
    get_configuration
    deploy_infrastructure
    set_user_password
    show_deployment_info
    
    # Ask if user wants to run tests
    echo
    read -p "Do you want to run automated tests? (y/N): " RUN_TESTS
    if [[ $RUN_TESTS =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    print_success "All done! 🎉"
}

# Handle script arguments
case "${1:-}" in
    "destroy")
        print_warning "Destroying infrastructure..."
        terraform destroy -var-file=terraform.tfvars -auto-approve
        print_success "Infrastructure destroyed."
        ;;
    "plan")
        terraform plan -var-file=terraform.tfvars
        ;;
    "output")
        terraform output
        ;;
    *)
        main
        ;;
esac