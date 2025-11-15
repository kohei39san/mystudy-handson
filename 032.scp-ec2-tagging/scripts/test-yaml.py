#!/usr/bin/env python3
"""
Simple YAML validation test for the CloudFormation template
"""

import yaml
import json
import sys
import os

def test_yaml_syntax():
    """Test YAML syntax of the CloudFormation template"""
    template_path = "../cfn/scp-ec2-tagging.yaml"
    
    if not os.path.exists(template_path):
        print(f"❌ Template file not found: {template_path}")
        return False
    
    try:
        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)
        
        print("✅ YAML syntax is valid")
        
        # Basic structure validation
        required_sections = ['AWSTemplateFormatVersion', 'Description', 'Resources']
        for section in required_sections:
            if section not in template:
                print(f"⚠️ Missing required section: {section}")
            else:
                print(f"✅ Found section: {section}")
        
        # Check for SCP policy
        resources = template.get('Resources', {})
        scp_found = False
        for resource_name, resource in resources.items():
            if resource.get('Type') == 'AWS::Organizations::Policy':
                print(f"✅ Found SCP resource: {resource_name}")
                scp_found = True
                
                # Check policy content
                content = resource.get('Properties', {}).get('Content')
                if content:
                    try:
                        # Try to parse the policy content as JSON
                        policy_json = json.loads(content.replace('!Sub |', '').strip())
                        print("✅ Policy content is valid JSON")
                        
                        # Check for required statements
                        statements = policy_json.get('Statement', [])
                        print(f"✅ Found {len(statements)} policy statements")
                        
                        for i, stmt in enumerate(statements):
                            effect = stmt.get('Effect')
                            actions = stmt.get('Action', [])
                            print(f"  Statement {i+1}: {effect} - {len(actions)} actions")
                        
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Policy content JSON validation failed: {e}")
        
        if not scp_found:
            print("❌ No SCP policy resource found")
            return False
        
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == '__main__':
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("========================================")
    print("CloudFormation Template Validation")
    print("========================================")
    
    if test_yaml_syntax():
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Validation failed!")
        sys.exit(1)