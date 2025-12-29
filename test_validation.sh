#!/bin/bash

echo "Testing CloudFormation template validation..."

# Test aurora.yaml
echo "=== Validating aurora.yaml ==="
python3 /workspace/validate_cfn.py /workspace/035.aurora-mock-testing/cfn/aurora.yaml

echo ""

# Test lambda.yaml  
echo "=== Validating lambda.yaml ==="
python3 /workspace/validate_cfn.py /workspace/035.aurora-mock-testing/cfn/lambda.yaml

echo ""
echo "Validation complete!"