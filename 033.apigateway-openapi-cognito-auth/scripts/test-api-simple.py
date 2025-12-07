#!/usr/bin/env python3
"""Simple API test script without emojis"""

import json
import requests
import boto3
import argparse
import sys

def test_api(api_endpoint, user_pool_id, client_id):
    cognito_client = boto3.client('cognito-idp', region_name='ap-northeast-1')
    
    print("Testing API Gateway OpenAPI Cognito Auth")
    print("=" * 60)
    
    # Authenticate users
    users = [
        {"username": "testuser", "password": "pkh1IJjHQTR-Y$2a", "role": "user"},
        {"username": "adminuser", "password": "fRCu#AKgQtmn3oxT", "role": "admin"}
    ]
    
    for user in users:
        print(f"\nAuthenticating {user['username']}...")
        
        try:
            response = cognito_client.admin_initiate_auth(
                UserPoolId=user_pool_id,
                ClientId=client_id,
                AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': user['username'],
                    'PASSWORD': user['password']
                }
            )
            
            token = response['AuthenticationResult']['IdToken']
            print(f"[OK] Authenticated successfully")
            
            # Test /health endpoint
            print(f"\nTesting /health endpoint...")
            resp = requests.get(f"{api_endpoint}/health", timeout=10)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Response: {resp.json()}")
            
            # Test /public endpoint
            print(f"\nTesting /public endpoint as {user['username']}...")
            headers = {'Authorization': f'Bearer {token}'}
            resp = requests.get(f"{api_endpoint}/public", headers=headers, timeout=10)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Message: {resp.json().get('message')}")
            
            # Test /user endpoint
            print(f"\nTesting /user endpoint as {user['username']}...")
            resp = requests.get(f"{api_endpoint}/user?limit=3", headers=headers, timeout=10)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Items returned: {len(data.get('data', []))}")
            
            # Test /admin endpoint
            print(f"\nTesting /admin endpoint as {user['username']}...")
            body = {"data": {"test": "value"}}
            resp = requests.post(f"{api_endpoint}/admin?action=create", 
                               headers=headers, json=body, timeout=10)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Message: {resp.json().get('message')}")
            elif resp.status_code == 403:
                print(f"[Expected] Access denied for {user['role']}")
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
    
    print("\n" + "=" * 60)
    print("[OK] Test completed!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-endpoint', required=True)
    parser.add_argument('--user-pool-id', required=True)
    parser.add_argument('--client-id', required=True)
    args = parser.parse_args()
    
    try:
        test_api(args.api_endpoint, args.user_pool_id, args.client_id)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        sys.exit(1)
