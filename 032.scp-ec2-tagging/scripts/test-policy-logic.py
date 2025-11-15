#!/usr/bin/env python3
"""
Test script to validate SCP policy logic
"""

import json
import yaml
import os

def load_policy_from_template():
    """Load the SCP policy from CloudFormation template"""
    template_path = "../cfn/scp-ec2-tagging.yaml"
    
    with open(template_path, 'r') as f:
        template = yaml.safe_load(f)
    
    resources = template.get('Resources', {})
    for resource_name, resource in resources.items():
        if resource.get('Type') == 'AWS::Organizations::Policy':
            content = resource.get('Properties', {}).get('Content', '')
            # Remove CloudFormation intrinsic function
            content = content.replace('!Sub |', '').strip()
            return json.loads(content)
    
    return None

def test_policy_logic():
    """Test the policy logic"""
    print("========================================")
    print("SCP Policy Logic Validation")
    print("========================================")
    
    policy = load_policy_from_template()
    if not policy:
        print("❌ Could not load policy from template")
        return False
    
    print("✅ Policy loaded successfully")
    
    statements = policy.get('Statement', [])
    print(f"✅ Found {len(statements)} statements")
    
    # Test scenarios
    test_scenarios = [
        {
            'name': 'EC2 launch in ap-northeast-1 with all required tags',
            'action': 'ec2:RunInstances',
            'region': 'ap-northeast-1',
            'tags': {'Name': 'test', 'Environment': 'dev', 'Owner': 'user@example.com'},
            'expected': 'ALLOW'
        },
        {
            'name': 'EC2 launch in us-east-1 (should be denied)',
            'action': 'ec2:RunInstances',
            'region': 'us-east-1',
            'tags': {'Name': 'test', 'Environment': 'dev', 'Owner': 'user@example.com'},
            'expected': 'DENY'
        },
        {
            'name': 'EC2 launch without Name tag',
            'action': 'ec2:RunInstances',
            'region': 'ap-northeast-1',
            'tags': {'Environment': 'dev', 'Owner': 'user@example.com'},
            'expected': 'DENY'
        },
        {
            'name': 'EC2 launch without Environment tag',
            'action': 'ec2:RunInstances',
            'region': 'ap-northeast-1',
            'tags': {'Name': 'test', 'Owner': 'user@example.com'},
            'expected': 'DENY'
        },
        {
            'name': 'EC2 launch without Owner tag',
            'action': 'ec2:RunInstances',
            'region': 'ap-northeast-1',
            'tags': {'Name': 'test', 'Environment': 'dev'},
            'expected': 'DENY'
        },
        {
            'name': 'Network interface creation (should be allowed)',
            'action': 'ec2:CreateNetworkInterface',
            'region': 'ap-northeast-1',
            'tags': {},
            'expected': 'ALLOW'
        }
    ]
    
    print("\n📋 Testing policy scenarios:")
    print("=" * 50)
    
    for scenario in test_scenarios:
        print(f"\n🧪 Test: {scenario['name']}")
        result = evaluate_policy(policy, scenario)
        
        if result == scenario['expected']:
            print(f"✅ PASS - Expected {scenario['expected']}, got {result}")
        else:
            print(f"❌ FAIL - Expected {scenario['expected']}, got {result}")
    
    return True

def evaluate_policy(policy, scenario):
    """
    Simplified policy evaluation logic
    Note: This is a basic simulation and doesn't cover all AWS policy evaluation nuances
    """
    action = scenario['action']
    region = scenario['region']
    tags = scenario['tags']
    
    # Check each statement
    for statement in policy['Statement']:
        if statement['Effect'] == 'Deny':
            # Check if action matches
            actions = statement.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            
            if action not in actions:
                continue
            
            # Check conditions
            conditions = statement.get('Condition', {})
            
            # Region check
            if 'StringNotEquals' in conditions:
                region_condition = conditions['StringNotEquals'].get('aws:RequestedRegion')
                if region_condition and region != region_condition:
                    return 'DENY'
            
            # Tag checks
            if 'Null' in conditions:
                for tag_key, should_be_null in conditions['Null'].items():
                    if tag_key.startswith('aws:RequestTag/'):
                        tag_name = tag_key.replace('aws:RequestTag/', '')
                        tag_exists = tag_name in tags and tags[tag_name]
                        
                        if should_be_null == "true" and tag_exists:
                            continue  # Tag exists, condition not met
                        elif should_be_null == "true" and not tag_exists:
                            return 'DENY'  # Tag missing, deny
    
    return 'ALLOW'

if __name__ == '__main__':
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        test_policy_logic()
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        exit(1)