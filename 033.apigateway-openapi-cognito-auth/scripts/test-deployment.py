#!/usr/bin/env python3
"""
API Gateway OpenAPI Cognito Auth - Deployment Test Script

This script tests the deployed API Gateway endpoints and validates the authentication flow.
"""

import json
import requests
import boto3
import argparse
import sys
from urllib.parse import urljoin
import base64

def decode_token(token):
    """Decode JWT token claims"""
    try:
        parts = token.split('.')
        if len(parts) < 2:
            return None
        
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def test_health_endpoint(api_endpoint):
    """Test /health endpoint (no authentication required)"""
    print("\n" + "=" * 70)
    print("TEST 1: Health Check Endpoint (No Authentication)")
    print("=" * 70)
    
    try:
        url = api_endpoint.rstrip('/') + '/health'
        print(f"GET {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("[PASS] Health endpoint is working")
            return True
        else:
            print(f"[FAIL] Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_authentication(user_pool_id, client_id, username, password, expected_role):
    """Test Cognito authentication"""
    print(f"\n" + "=" * 70)
    print(f"TEST: Authentication - {username}")
    print("=" * 70)
    
    cognito_client = boto3.client('cognito-idp', region_name='ap-northeast-1')
    
    try:
        print(f"Authenticating {username}...")
        
        response = cognito_client.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        if 'AuthenticationResult' not in response:
            print(f"[FAIL] Authentication failed: {response}")
            return None
        
        auth_result = response['AuthenticationResult']
        access_token = auth_result.get('AccessToken')
        id_token = auth_result.get('IdToken')
        
        print(f"[PASS] Authentication successful")
        
        # Decode and display token claims
        id_claims = decode_token(id_token)
        if id_claims:
            print(f"\nID Token Claims:")
            print(f"  Username: {id_claims.get('cognito:username')}")
            print(f"  Email: {id_claims.get('email')}")
            print(f"  Custom Role: {id_claims.get('custom:role')}")
            print(f"  Groups: {id_claims.get('cognito:groups', [])}")
            
            actual_role = id_claims.get('custom:role')
            if actual_role == expected_role:
                print(f"[PASS] Role verification: {actual_role}")
            else:
                print(f"[WARN] Role mismatch. Expected: {expected_role}, Got: {actual_role}")
        
        return {
            'access_token': access_token,
            'id_token': id_token,
            'username': username
        }
    
    except Exception as e:
        print(f"[FAIL] Authentication error: {e}")
        return None

def test_public_endpoint(api_endpoint, auth_info):
    """Test /public endpoint (authentication required)"""
    print(f"\n" + "=" * 70)
    print(f"TEST: Public Endpoint - {auth_info['username']}")
    print("=" * 70)
    
    try:
        url = api_endpoint.rstrip('/') + '/public'
        headers = {
            'Authorization': f"Bearer {auth_info['id_token']}",
            'Content-Type': 'application/json'
        }
        
        print(f"GET {url}")
        print(f"Headers: Authorization: Bearer {auth_info['id_token'][:30]}...")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print(f"[PASS] Public endpoint accessible for {auth_info['username']}")
            return True
        elif response.status_code == 403:
            print(f"[WARN] Access forbidden (403): {response.text}")
            return False
        else:
            print(f"[FAIL] Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_user_endpoint(api_endpoint, auth_info):
    """Test /user endpoint (user role required)"""
    print(f"\n" + "=" * 70)
    print(f"TEST: User Endpoint - {auth_info['username']}")
    print("=" * 70)
    
    try:
        url = api_endpoint.rstrip('/') + '/user'
        headers = {
            'Authorization': f"Bearer {auth_info['id_token']}",
            'Content-Type': 'application/json'
        }
        
        print(f"GET {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print(f"[PASS] User endpoint accessible for {auth_info['username']}")
            return True
        elif response.status_code == 403:
            print(f"[INFO] Access forbidden (403) - expected if not in user role")
            return False
        else:
            print(f"[FAIL] Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_admin_endpoint(api_endpoint, auth_info):
    """Test /admin endpoint (admin role required)"""
    print(f"\n" + "=" * 70)
    print(f"TEST: Admin Endpoint - {auth_info['username']}")
    print("=" * 70)
    
    try:
        url = api_endpoint.rstrip('/') + '/admin'
        headers = {
            'Authorization': f"Bearer {auth_info['id_token']}",
            'Content-Type': 'application/json'
        }
        
        print(f"POST {url}")
        
        response = requests.post(url, headers=headers, json={}, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print(f"[PASS] Admin endpoint accessible for {auth_info['username']}")
            return True
        elif response.status_code == 403:
            print(f"[INFO] Access forbidden (403) - expected if not in admin role")
            return False
        else:
            print(f"[FAIL] Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test API Gateway OpenAPI Cognito Auth Deployment')
    parser.add_argument('--api-endpoint', required=True, help='API Gateway endpoint URL')
    parser.add_argument('--user-pool-id', required=True, help='Cognito User Pool ID')
    parser.add_argument('--client-id', required=True, help='Cognito User Pool Client ID')
    
    args = parser.parse_args()
    
    api_endpoint = args.api_endpoint.rstrip('/')
    user_pool_id = args.user_pool_id
    client_id = args.client_id
    
    print("\n" + "=" * 70)
    print("API Gateway OpenAPI Cognito Auth - Deployment Test")
    print("=" * 70)
    print(f"API Endpoint: {api_endpoint}")
    print(f"User Pool ID: {user_pool_id}")
    print(f"Client ID: {client_id}")
    
    results = {
        'health': False,
        'testuser_auth': False,
        'adminuser_auth': False,
        'public_endpoint': False,
        'user_endpoint': False,
        'admin_endpoint': False
    }
    
    # Test health endpoint
    results['health'] = test_health_endpoint(api_endpoint)
    
    # Test authentication for test user
    testuser_auth = test_authentication(
        user_pool_id,
        client_id,
        'testuser',
        'TempPass123!@#',  # Test user password
        'user'
    )
    if testuser_auth:
        results['testuser_auth'] = True
        results['public_endpoint'] = test_public_endpoint(api_endpoint, testuser_auth)
        results['user_endpoint'] = test_user_endpoint(api_endpoint, testuser_auth)
        results['admin_endpoint'] = test_admin_endpoint(api_endpoint, testuser_auth)
    
    # Test authentication for admin user
    adminuser_auth = test_authentication(
        user_pool_id,
        client_id,
        'adminuser',
        'AdminPass123!@#',  # Admin user password
        'admin'
    )
    if adminuser_auth:
        results['adminuser_auth'] = True
        results['public_endpoint'] = test_public_endpoint(api_endpoint, adminuser_auth)
        results['user_endpoint'] = test_user_endpoint(api_endpoint, adminuser_auth)
        results['admin_endpoint'] = test_admin_endpoint(api_endpoint, adminuser_auth)
    
    # Print summary
    print(f"\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
