#!/usr/bin/env python3
"""
Simple CloudFormation template validator to check basic syntax and structure
"""
import yaml
import sys
import os

def validate_yaml_syntax(file_path):
    """Validate YAML syntax"""
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
        return True, "Valid YAML syntax"
    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def basic_cfn_validation(file_path):
    """Basic CloudFormation template validation"""
    try:
        with open(file_path, 'r') as f:
            template = yaml.safe_load(f)
        
        issues = []
        
        # Check for required sections
        if 'AWSTemplateFormatVersion' not in template:
            issues.append("Missing AWSTemplateFormatVersion")
        
        # Check for circular references in security groups (basic check)
        if 'Resources' in template:
            resources = template['Resources']
            sg_refs = {}
            
            for resource_name, resource in resources.items():
                if resource.get('Type') == 'AWS::EC2::SecurityGroup':
                    sg_refs[resource_name] = []
                    
                    # Check ingress rules
                    props = resource.get('Properties', {})
                    ingress_rules = props.get('SecurityGroupIngress', [])
                    if isinstance(ingress_rules, list):
                        for rule in ingress_rules:
                            if 'SourceSecurityGroupId' in rule:
                                ref = rule['SourceSecurityGroupId']
                                if isinstance(ref, dict) and ref.get('Ref'):
                                    sg_refs[resource_name].append(ref['Ref'])
                    
                    # Check egress rules
                    egress_rules = props.get('SecurityGroupEgress', [])
                    if isinstance(egress_rules, list):
                        for rule in egress_rules:
                            if 'DestinationSecurityGroupId' in rule:
                                ref = rule['DestinationSecurityGroupId']
                                if isinstance(ref, dict) and ref.get('Ref'):
                                    sg_refs[resource_name].append(ref['Ref'])
            
            # Check for circular dependencies
            for sg_name, refs in sg_refs.items():
                for ref in refs:
                    if ref in sg_refs and sg_name in sg_refs[ref]:
                        issues.append(f"Potential circular dependency between {sg_name} and {ref}")
        
        return len(issues) == 0, issues if issues else ["Template appears valid"]
        
    except Exception as e:
        return False, [f"Error validating template: {e}"]

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_cfn.py <cfn_template.yaml>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    print(f"Validating: {file_path}")
    
    # YAML syntax validation
    yaml_valid, yaml_msg = validate_yaml_syntax(file_path)
    print(f"YAML Syntax: {'✓' if yaml_valid else '✗'} {yaml_msg}")
    
    if not yaml_valid:
        sys.exit(1)
    
    # Basic CFN validation
    cfn_valid, cfn_issues = basic_cfn_validation(file_path)
    print(f"CloudFormation: {'✓' if cfn_valid else '✗'}")
    
    for issue in cfn_issues:
        print(f"  - {issue}")
    
    if not cfn_valid:
        sys.exit(1)
    
    print("✓ Validation passed!")

if __name__ == "__main__":
    main()