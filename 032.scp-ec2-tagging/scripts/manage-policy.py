#!/usr/bin/env python3
"""
SCP EC2 Tagging Enforcement - Policy Management Script
This script helps manage the SCP policy attachments and provides utilities
"""

import boto3
import json
import sys
import argparse
from botocore.exceptions import ClientError, NoCredentialsError

class SCPManager:
    def __init__(self, region='ap-northeast-1'):
        try:
            self.org_client = boto3.client('organizations', region_name=region)
            self.cfn_client = boto3.client('cloudformation', region_name=region)
            self.region = region
        except NoCredentialsError:
            print("❌ AWS credentials not configured. Please configure AWS CLI.")
            sys.exit(1)
    
    def get_policy_id_from_stack(self, stack_name='scp-ec2-tagging-enforcement'):
        """Get policy ID from CloudFormation stack outputs"""
        try:
            response = self.cfn_client.describe_stacks(StackName=stack_name)
            outputs = response['Stacks'][0]['Outputs']
            
            for output in outputs:
                if output['OutputKey'] == 'PolicyId':
                    return output['OutputValue']
            
            print(f"❌ PolicyId output not found in stack {stack_name}")
            return None
            
        except ClientError as e:
            print(f"❌ Error getting stack outputs: {e}")
            return None
    
    def list_organizational_units(self):
        """List all organizational units"""
        try:
            # Get root ID first
            roots = self.org_client.list_roots()['Roots']
            if not roots:
                print("❌ No organization roots found")
                return []
            
            root_id = roots[0]['Id']
            print(f"📋 Organization Root: {root_id}")
            
            # List OUs
            ous = []
            paginator = self.org_client.get_paginator('list_organizational_units_for_parent')
            
            for page in paginator.paginate(ParentId=root_id):
                ous.extend(page['OrganizationalUnits'])
            
            print(f"📋 Found {len(ous)} Organizational Units:")
            for ou in ous:
                print(f"  - {ou['Name']} ({ou['Id']})")
            
            return ous
            
        except ClientError as e:
            print(f"❌ Error listing OUs: {e}")
            return []
    
    def list_accounts_in_ou(self, ou_id):
        """List accounts in a specific OU"""
        try:
            accounts = []
            paginator = self.org_client.get_paginator('list_accounts_for_parent')
            
            for page in paginator.paginate(ParentId=ou_id):
                accounts.extend(page['Accounts'])
            
            print(f"📋 Accounts in OU {ou_id}:")
            for account in accounts:
                status = "✅" if account['Status'] == 'ACTIVE' else "⚠️"
                print(f"  {status} {account['Name']} ({account['Id']}) - {account['Status']}")
            
            return accounts
            
        except ClientError as e:
            print(f"❌ Error listing accounts: {e}")
            return []
    
    def attach_policy_to_ou(self, policy_id, ou_id):
        """Attach policy to organizational unit"""
        try:
            self.org_client.attach_policy(PolicyId=policy_id, TargetId=ou_id)
            print(f"✅ Policy {policy_id} attached to OU {ou_id}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'DuplicatePolicyAttachmentException':
                print(f"⚠️ Policy {policy_id} is already attached to OU {ou_id}")
                return True
            else:
                print(f"❌ Error attaching policy: {e}")
                return False
    
    def detach_policy_from_ou(self, policy_id, ou_id):
        """Detach policy from organizational unit"""
        try:
            self.org_client.detach_policy(PolicyId=policy_id, TargetId=ou_id)
            print(f"✅ Policy {policy_id} detached from OU {ou_id}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'PolicyNotAttachedException':
                print(f"⚠️ Policy {policy_id} is not attached to OU {ou_id}")
                return True
            else:
                print(f"❌ Error detaching policy: {e}")
                return False
    
    def list_policy_targets(self, policy_id):
        """List targets where policy is attached"""
        try:
            targets = []
            paginator = self.org_client.get_paginator('list_targets_for_policy')
            
            for page in paginator.paginate(PolicyId=policy_id):
                targets.extend(page['Targets'])
            
            if targets:
                print(f"📋 Policy {policy_id} is attached to:")
                for target in targets:
                    print(f"  - {target['Name']} ({target['TargetId']}) - {target['Type']}")
            else:
                print(f"📋 Policy {policy_id} is not attached to any targets")
            
            return targets
            
        except ClientError as e:
            print(f"❌ Error listing policy targets: {e}")
            return []
    
    def get_policy_details(self, policy_id):
        """Get policy details"""
        try:
            response = self.org_client.describe_policy(PolicyId=policy_id)
            policy = response['Policy']
            
            print(f"📋 Policy Details:")
            print(f"  Name: {policy['PolicySummary']['Name']}")
            print(f"  ID: {policy['PolicySummary']['Id']}")
            print(f"  Type: {policy['PolicySummary']['Type']}")
            print(f"  Description: {policy['PolicySummary']['Description']}")
            print(f"  ARN: {policy['PolicySummary']['Arn']}")
            
            return policy
            
        except ClientError as e:
            print(f"❌ Error getting policy details: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='SCP EC2 Tagging Policy Management')
    parser.add_argument('--region', default='ap-northeast-1', help='AWS region')
    parser.add_argument('--stack-name', default='scp-ec2-tagging-enforcement', 
                       help='CloudFormation stack name')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List OUs command
    subparsers.add_parser('list-ous', help='List organizational units')
    
    # List accounts command
    list_accounts_parser = subparsers.add_parser('list-accounts', help='List accounts in OU')
    list_accounts_parser.add_argument('ou_id', help='Organizational Unit ID')
    
    # Attach policy command
    attach_parser = subparsers.add_parser('attach', help='Attach policy to OU')
    attach_parser.add_argument('ou_id', help='Organizational Unit ID')
    attach_parser.add_argument('--policy-id', help='Policy ID (auto-detected from stack if not provided)')
    
    # Detach policy command
    detach_parser = subparsers.add_parser('detach', help='Detach policy from OU')
    detach_parser.add_argument('ou_id', help='Organizational Unit ID')
    detach_parser.add_argument('--policy-id', help='Policy ID (auto-detected from stack if not provided)')
    
    # List targets command
    targets_parser = subparsers.add_parser('list-targets', help='List policy targets')
    targets_parser.add_argument('--policy-id', help='Policy ID (auto-detected from stack if not provided)')
    
    # Policy details command
    details_parser = subparsers.add_parser('policy-details', help='Show policy details')
    details_parser.add_argument('--policy-id', help='Policy ID (auto-detected from stack if not provided)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = SCPManager(region=args.region)
    
    # Get policy ID if not provided
    policy_id = getattr(args, 'policy_id', None)
    if not policy_id and args.command in ['attach', 'detach', 'list-targets', 'policy-details']:
        policy_id = manager.get_policy_id_from_stack(args.stack_name)
        if not policy_id:
            print("❌ Could not determine policy ID. Please provide --policy-id")
            return
    
    # Execute commands
    if args.command == 'list-ous':
        manager.list_organizational_units()
    
    elif args.command == 'list-accounts':
        manager.list_accounts_in_ou(args.ou_id)
    
    elif args.command == 'attach':
        manager.attach_policy_to_ou(policy_id, args.ou_id)
    
    elif args.command == 'detach':
        manager.detach_policy_from_ou(policy_id, args.ou_id)
    
    elif args.command == 'list-targets':
        manager.list_policy_targets(policy_id)
    
    elif args.command == 'policy-details':
        manager.get_policy_details(policy_id)

if __name__ == '__main__':
    main()