#!/bin/bash

# SCP EC2 Tagging Enforcement - Help Script
# This script provides help and usage information

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BOLD}${BLUE}$1${NC}"
}

print_subheader() {
    echo -e "${BOLD}$1${NC}"
}

print_command() {
    echo -e "  ${GREEN}$1${NC}"
}

print_description() {
    echo -e "    $1"
}

print_warning() {
    echo -e "${YELLOW}⚠ WARNING:${NC} $1"
}

print_note() {
    echo -e "${CYAN}📝 NOTE:${NC} $1"
}

# Main help function
show_help() {
    echo "=========================================="
    print_header "SCP EC2 Tagging Enforcement - Help"
    echo "=========================================="
    echo ""
    
    print_subheader "OVERVIEW"
    echo "This CloudFormation template creates an AWS Organizations Service Control Policy (SCP)"
    echo "that enforces tagging requirements for EC2 instances while allowing related resources"
    echo "to be created without tags."
    echo ""
    
    print_subheader "AVAILABLE SCRIPTS"
    echo ""
    
    print_command "./validate-template.sh"
    print_description "Validates the CloudFormation template syntax and content"
    print_description "Checks for common issues and displays template summary"
    echo ""
    
    print_command "./deploy.sh"
    print_description "Deploys the SCP CloudFormation stack"
    print_description "Creates or updates the stack and SCP policy"
    echo ""
    
    print_command "./cleanup.sh"
    print_description "Removes the CloudFormation stack and SCP policy"
    print_description "Automatically detaches policy from targets if needed"
    echo ""
    
    print_command "./help.sh"
    print_description "Shows this help information"
    echo ""
    
    print_subheader "TYPICAL WORKFLOW"
    echo ""
    echo "1. Validate the template:"
    print_command "   ./validate-template.sh"
    echo ""
    echo "2. Deploy the stack:"
    print_command "   ./deploy.sh"
    echo ""
    echo "3. Attach policy to organizational units (manual step)"
    echo ""
    echo "4. Test in non-production environment"
    echo ""
    echo "5. When no longer needed, cleanup:"
    print_command "   ./cleanup.sh"
    echo ""
    
    print_subheader "POLICY DETAILS"
    echo ""
    echo "The SCP policy enforces the following requirements:"
    echo ""
    echo "• Required Tags for EC2 Instances:"
    echo "  - Name: Instance name"
    echo "  - Environment: Environment identifier (dev, staging, prod, etc.)"
    echo "  - Owner: Owner information"
    echo ""
    echo "• Allowed without tags:"
    echo "  - Network Interfaces (NICs)"
    echo "  - EC2 Instance Connect Endpoints (EICE)"
    echo "  - Security Groups"
    echo "  - Key Pairs"
    echo "  - Placement Groups"
    echo ""
    
    print_subheader "PREREQUISITES"
    echo ""
    echo "• AWS CLI installed and configured"
    echo "• AWS Organizations management account access"
    echo "• Appropriate IAM permissions:"
    echo "  - organizations:CreatePolicy"
    echo "  - organizations:AttachPolicy"
    echo "  - organizations:DetachPolicy"
    echo "  - organizations:DeletePolicy"
    echo "  - cloudformation:* (for stack operations)"
    echo ""
    
    print_subheader "MANUAL STEPS AFTER DEPLOYMENT"
    echo ""
    echo "After deploying the stack, you need to manually attach the policy:"
    echo ""
    echo "1. Get the Policy ID from the stack outputs"
    echo "2. Attach to organizational unit:"
    print_command "   aws organizations attach-policy --policy-id <POLICY_ID> --target-id <OU_ID>"
    echo ""
    echo "3. Or use the AWS Organizations console:"
    echo "   - Navigate to AWS Organizations"
    echo "   - Go to Policies > Service control policies"
    echo "   - Find your policy and attach to desired OUs"
    echo ""
    
    print_subheader "TESTING THE POLICY"
    echo ""
    echo "To test if the policy is working:"
    echo ""
    echo "1. Try creating an EC2 instance without required tags (should fail):"
    print_command "   aws ec2 run-instances --image-id ami-12345 --instance-type t3.micro"
    echo ""
    echo "2. Try creating an EC2 instance with required tags (should succeed):"
    print_command "   aws ec2 run-instances --image-id ami-12345 --instance-type t3.micro \\"
    print_command "     --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=test},"
    print_command "     {Key=Environment,Value=dev},{Key=Owner,Value=user@example.com}]'"
    echo ""
    
    print_subheader "TROUBLESHOOTING"
    echo ""
    echo "Common issues and solutions:"
    echo ""
    echo "• Policy not taking effect:"
    echo "  - Verify policy is attached to the correct OU"
    echo "  - Check if account is in the target OU"
    echo "  - Wait a few minutes for policy propagation"
    echo ""
    echo "• Template validation errors:"
    echo "  - Check YAML syntax"
    echo "  - Verify AWS CLI configuration"
    echo "  - Ensure proper IAM permissions"
    echo ""
    echo "• Deployment failures:"
    echo "  - Confirm you're in the Organizations management account"
    echo "  - Check CloudFormation events for detailed error messages"
    echo "  - Verify region settings (ap-northeast-1)"
    echo ""
    
    print_subheader "IMPORTANT WARNINGS"
    echo ""
    print_warning "This policy will prevent EC2 instance creation without required tags!"
    print_warning "Test thoroughly in non-production environments first."
    print_warning "Ensure emergency procedures are in place before applying to production."
    echo ""
    
    print_note "Policy changes may take a few minutes to propagate across AWS services."
    print_note "Monitor CloudTrail logs for denied actions after applying the policy."
    echo ""
    
    print_subheader "SUPPORT AND DOCUMENTATION"
    echo ""
    echo "• AWS Organizations SCP Documentation:"
    echo "  https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html"
    echo ""
    echo "• EC2 Tag-based Access Control:"
    echo "  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/control-access-with-tags.html"
    echo ""
    echo "• CloudFormation Organizations Policy Reference:"
    echo "  https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-organizations-policy.html"
    echo ""
    
    echo "=========================================="
    print_header "End of Help"
    echo "=========================================="
}

# Run help function
show_help