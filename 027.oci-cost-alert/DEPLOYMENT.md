# OCI Cost Alert - Deployment Guide

## Quick Start

### 1. Prerequisites

- Terraform >= 1.0.0 installed
- OCI CLI configured or environment variables set
- Valid OCI compartment with appropriate permissions

### 2. Configuration

```bash
# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
vim terraform.tfvars
```

Required variables:
- `compartment_id`: Your OCI compartment OCID
- `alert_email`: Email address for notifications

### 3. Validation

```bash
# Run comprehensive validation
bash scripts/validate.sh

# Run all tests
bash scripts/test.sh
```

### 4. Deployment

```bash
# Initialize Terraform
terraform init

# Review execution plan
terraform plan

# Apply configuration
terraform apply
```

### 5. Post-Deployment

1. Check your email for ONS subscription confirmation
2. Click the confirmation link to activate notifications
3. Test the alert by monitoring your OCI spending

## Testing

### Unit Tests
```bash
bash tests/unit_test.sh
```

### Integration Tests
```bash
bash tests/integration_test.sh
```

### All Tests
```bash
bash scripts/test.sh
```

## Cleanup

```bash
# Destroy all resources
bash scripts/cleanup.sh

# Or manually
terraform destroy
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Ensure OCI CLI is configured: `oci setup config`
   - Or set environment variables: `OCI_TENANCY_OCID`, `OCI_USER_OCID`, etc.

2. **Permission Denied**
   - Verify IAM policies for Budget and ONS services
   - Check compartment access permissions

3. **Email Not Received**
   - Check spam folder
   - Verify email address in terraform.tfvars
   - Check ONS subscription status in OCI console

4. **Budget Not Triggering**
   - Ensure spending exceeds threshold
   - Check budget configuration in OCI console
   - Verify alert rules are active

### Support

For issues specific to this configuration:
1. Check the README.md for detailed documentation
2. Run validation scripts to identify configuration issues
3. Review Terraform logs for detailed error messages

For OCI-specific issues:
- [OCI Documentation](https://docs.oracle.com/en-us/iaas/)
- [OCI Support](https://www.oracle.com/support/)