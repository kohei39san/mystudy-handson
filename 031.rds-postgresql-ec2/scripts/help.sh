#!/bin/bash

# Help Script - Shows all available commands and usage
# This script provides a quick reference for all available operations

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== RDS PostgreSQL with EC2 - Available Commands ===${NC}"
echo ""

echo -e "${GREEN}📋 SETUP AND DEPLOYMENT${NC}"
echo -e "${CYAN}./validate-template.sh${NC}    - Validate CloudFormation template syntax"
echo -e "${CYAN}./deploy.sh${NC}               - Deploy the complete infrastructure stack"
echo -e "${CYAN}./check-status.sh${NC}         - Check status of deployed resources"
echo ""

echo -e "${GREEN}🔧 MANAGEMENT${NC}"
echo -e "${CYAN}./cleanup.sh${NC}              - Delete all resources and clean up"
echo -e "${CYAN}./help.sh${NC}                 - Show this help message"
echo ""

echo -e "${GREEN}🧪 TESTING (Run on EC2 instance)${NC}"
echo -e "${CYAN}./test-connection.sh${NC}      - Test RDS connectivity and authentication"
echo ""

echo -e "${GREEN}📖 QUICK START GUIDE${NC}"
echo "1. Make scripts executable:"
echo "   ${YELLOW}chmod +x scripts/*.sh${NC}"
echo ""
echo "2. Validate template:"
echo "   ${YELLOW}cd scripts && ./validate-template.sh${NC}"
echo ""
echo "3. Deploy infrastructure:"
echo "   ${YELLOW}./deploy.sh${NC}"
echo ""
echo "4. Check deployment status:"
echo "   ${YELLOW}./check-status.sh${NC}"
echo ""
echo "5. Connect to EC2 via Systems Manager:"
echo "   ${YELLOW}aws ssm start-session --target <INSTANCE-ID> --region ap-northeast-1${NC}"
echo ""
echo "6. Test connections on EC2:"
echo "   ${YELLOW}./test-connection.sh${NC}"
echo ""
echo "7. Clean up when done:"
echo "   ${YELLOW}./cleanup.sh${NC}"
echo ""

echo -e "${GREEN}🔗 CONNECTION SCRIPTS (Available on EC2)${NC}"
echo -e "${CYAN}./connect-to-rds.sh${NC}       - Connect using password authentication (Secrets Manager)"
echo -e "${CYAN}./connect-to-rds-iam.sh${NC}   - Connect using IAM authentication"
echo -e "${CYAN}source rds-env.sh${NC}         - Load RDS connection environment variables"
echo ""

echo -e "${GREEN}📚 DOCUMENTATION${NC}"
echo "For detailed information, see: ${YELLOW}../README.md${NC}"
echo ""

echo -e "${GREEN}⚠️  IMPORTANT NOTES${NC}"
echo "• This setup is optimized for cost (development/testing)"
echo "• RDS instance takes 5-10 minutes to become available"
echo "• Database password is automatically generated and stored in AWS Secrets Manager"
echo "• IAM authentication requires database user setup"
echo "• All resources are created in ap-northeast-1 region"
echo ""

echo -e "${BLUE}=== End of Help ===${NC}"