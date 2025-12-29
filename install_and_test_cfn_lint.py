#!/usr/bin/env python3

import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main():
    print("Attempting to install and run cfn-lint...")
    
    # Try to install cfn-lint
    print("Installing cfn-lint...")
    ret_code, stdout, stderr = run_command("python3 -m pip install --user cfn-lint")
    
    if ret_code != 0:
        print(f"Failed to install cfn-lint: {stderr}")
        return 1
    
    print("cfn-lint installed successfully")
    
    # Add ~/.local/bin to PATH
    os.environ['PATH'] = f"{os.path.expanduser('~/.local/bin')}:{os.environ.get('PATH', '')}"
    
    # Test aurora.yaml
    print("\n=== Running cfn-lint on aurora.yaml ===")
    ret_code, stdout, stderr = run_command("cfn-lint /workspace/035.aurora-mock-testing/cfn/aurora.yaml")
    
    if ret_code == 0:
        print("✓ aurora.yaml passed cfn-lint validation!")
    else:
        print("✗ aurora.yaml failed cfn-lint validation:")
        print(stdout)
        print(stderr)
    
    # Test lambda.yaml
    print("\n=== Running cfn-lint on lambda.yaml ===")
    ret_code, stdout, stderr = run_command("cfn-lint /workspace/035.aurora-mock-testing/cfn/lambda.yaml")
    
    if ret_code == 0:
        print("✓ lambda.yaml passed cfn-lint validation!")
    else:
        print("✗ lambda.yaml failed cfn-lint validation:")
        print(stdout)
        print(stderr)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())