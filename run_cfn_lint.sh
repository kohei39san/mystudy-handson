#!/bin/bash

echo "Installing cfn-lint..."

# Try to install cfn-lint
python3 -m pip install --user cfn-lint

# Check if installation was successful
if command -v cfn-lint &> /dev/null; then
    echo "cfn-lint installed successfully"
    
    echo "Running cfn-lint on aurora.yaml..."
    cfn-lint /workspace/035.aurora-mock-testing/cfn/aurora.yaml
    
    echo ""
    echo "Running cfn-lint on lambda.yaml..."
    cfn-lint /workspace/035.aurora-mock-testing/cfn/lambda.yaml
    
else
    echo "cfn-lint installation failed, trying alternative approach..."
    
    # Try with ~/.local/bin in PATH
    export PATH="$HOME/.local/bin:$PATH"
    
    if command -v cfn-lint &> /dev/null; then
        echo "cfn-lint found in ~/.local/bin"
        
        echo "Running cfn-lint on aurora.yaml..."
        cfn-lint /workspace/035.aurora-mock-testing/cfn/aurora.yaml
        
        echo ""
        echo "Running cfn-lint on lambda.yaml..."
        cfn-lint /workspace/035.aurora-mock-testing/cfn/lambda.yaml
    else
        echo "cfn-lint not available, using basic validation..."
        
        echo "=== Validating aurora.yaml ==="
        python3 /workspace/validate_cfn.py /workspace/035.aurora-mock-testing/cfn/aurora.yaml
        
        echo ""
        echo "=== Validating lambda.yaml ==="
        python3 /workspace/validate_cfn.py /workspace/035.aurora-mock-testing/cfn/lambda.yaml
    fi
fi