# Infrastructure Directory Analysis

## Directories with existing diagrams (src/architecture.drawio and src/architecture.svg):
- 001.ec2-ec2,ec2 ✅
- 002.ec2windows ✅
- 003.minikube-opensearch,prometheus ✅
- 004.RDS_instance ✅
- 011.cfn ✅
- 013.aws-github-oidc ✅
- 031.rds-postgresql-ec2 ✅

## Directories that need diagrams created:

### AWS-based directories (use aws-template.drawio):
- 010.ec2-linux-latest-eice (has Terraform files, comprehensive README, no diagram)
- 030.apigateway-cognito-lambda-payload (has Terraform + CloudFormation, comprehensive README, no diagram)
- 032.scp-ec2-tagging (has CloudFormation, README, no diagram)
- 033.apigateway-openapi-cognito-auth (has CloudFormation, README, no diagram)
- 035.aurora-mock-testing (has Terraform + CloudFormation, comprehensive README, no diagram)
- 036.scp-owner-tag-enforcement (has CloudFormation, README, no diagram)

### OCI-based directories (use oci-template.svg):
- 028.oci-bucket-tfstate (has Terraform files, good README, no diagram)
- 029.oci-cost-alert (has Terraform files, README, no diagram)

### Non-infrastructure directories (no diagrams needed):
- 034.redmine-mcp-server (Python application, no infrastructure)

## Directories to check further:
Need to check directories 005-009, 012, 014-027 to complete the analysis.