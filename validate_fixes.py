#!/usr/bin/env python3

import yaml
import sys

def validate_yaml_files():
    files_to_check = [
        "/workspace/035.aurora-mock-testing/cfn/aurora.yaml",
        "/workspace/035.aurora-mock-testing/cfn/lambda.yaml"
    ]
    
    all_valid = True
    
    for file_path in files_to_check:
        print(f"\n=== Validating {file_path} ===")
        
        try:
            with open(file_path, 'r') as f:
                content = yaml.safe_load(f)
            
            print("✓ YAML syntax is valid")
            
            # Basic CloudFormation checks
            if 'AWSTemplateFormatVersion' not in content:
                print("✗ Missing AWSTemplateFormatVersion")
                all_valid = False
            else:
                print("✓ Has AWSTemplateFormatVersion")
            
            if 'Resources' not in content:
                print("✗ Missing Resources section")
                all_valid = False
            else:
                print(f"✓ Has Resources section with {len(content['Resources'])} resources")
            
            # Check for our specific fixes
            if 'aurora.yaml' in file_path:
                resources = content.get('Resources', {})
                
                # Check if we have separate security group rules
                if 'AuroraIngressFromLambda' in resources:
                    print("✓ Found separate Aurora ingress rule (circular dependency fix)")
                else:
                    print("✗ Missing separate Aurora ingress rule")
                    all_valid = False
                
                # Check Aurora engine version
                aurora_cluster = resources.get('AuroraCluster', {})
                engine_version = aurora_cluster.get('Properties', {}).get('EngineVersion')
                if engine_version == '15.5':
                    print("✓ Aurora engine version updated to 15.5")
                elif engine_version == '15.4':
                    print("✗ Aurora engine version still at deprecated 15.4")
                    all_valid = False
                else:
                    print(f"? Aurora engine version: {engine_version}")
            
            elif 'lambda.yaml' in file_path:
                # Check if VpcId parameter was removed
                parameters = content.get('Parameters', {})
                if 'VpcId' not in parameters:
                    print("✓ Unused VpcId parameter removed")
                else:
                    print("✗ VpcId parameter still present")
                    all_valid = False
                
                # Check Lambda layer configuration
                resources = content.get('Resources', {})
                lambda_layer = resources.get('LambdaLayer', {})
                layer_content = lambda_layer.get('Properties', {}).get('Content', {})
                
                if 'S3Bucket' in layer_content and 'S3Key' in layer_content:
                    print("✓ Lambda layer uses S3Bucket/S3Key configuration")
                elif 'ZipFile' in layer_content:
                    print("? Lambda layer still uses ZipFile (may cause cfn-lint warning)")
                
                # Check environment variables
                lambda_func = resources.get('LambdaFunction', {})
                env_vars = lambda_func.get('Properties', {}).get('Environment', {}).get('Variables', {})
                
                if 'AWS_REGION' not in env_vars and 'CURRENT_REGION' in env_vars:
                    print("✓ Reserved AWS_REGION variable replaced with CURRENT_REGION")
                elif 'AWS_REGION' in env_vars:
                    print("✗ Reserved AWS_REGION variable still present")
                    all_valid = False
                else:
                    print("? Environment variables configuration unclear")
            
        except yaml.YAMLError as e:
            print(f"✗ YAML syntax error: {e}")
            all_valid = False
        except Exception as e:
            print(f"✗ Error reading file: {e}")
            all_valid = False
    
    print(f"\n=== Summary ===")
    if all_valid:
        print("✓ All validations passed!")
        return 0
    else:
        print("✗ Some validations failed")
        return 1

if __name__ == "__main__":
    sys.exit(validate_yaml_files())