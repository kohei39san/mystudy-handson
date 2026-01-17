#!/usr/bin/env python3
"""
Login Test Script for API Gateway OpenAPI Cognito Auth

This script tests the /auth/login endpoint and displays all response headers
"""

import json
import requests
import argparse
import sys


def test_login(api_endpoint, username, password):
    """Test /auth/login endpoint"""
    print("\n" + "=" * 80)
    print("API Gateway OpenAPI Cognito Auth - Login Test")
    print("=" * 80)
    print(f"API Endpoint: {api_endpoint}")
    print(f"Username: {username}")
    
    try:
        url = api_endpoint.rstrip('/') + '/auth/login'
        payload = {
            'username': username,
            'password': password
        }
        
        print(f"\nPOST {url}")
        print("Request Body: [username and password omitted from logs]")
        
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"\n" + "=" * 80)
        print("RESPONSE")
        print("=" * 80)
        print(f"Status Code: {response.status_code}")
        
        print(f"\nResponse Headers:")
        print("-" * 80)
        for header_name, header_value in response.headers.items():
            if len(header_value) > 100:
                print(f"  {header_name}: {header_value[:100]}...")
            else:
                print(f"  {header_name}: {header_value}")
        
        print(f"\nResponse Body:")
        print("-" * 80)
        try:
            body = response.json()
            print(json.dumps(body, indent=2))
        except:
            print(response.text)
        
        if response.status_code == 200:
            print(f"\n[PASS] Login successful")
            
            # Check for expected headers
            print(f"\n" + "=" * 80)
            print("TOKEN HEADERS")
            print("=" * 80)
            
            auth_header = response.headers.get('Authorization')
            remapped_auth = response.headers.get('x-amzn-Remapped-Authorization')
            id_token_header = response.headers.get('X-ID-Token')
            refresh_token_header = response.headers.get('X-Refresh-Token')
            expires_in_header = response.headers.get('X-Expires-In')
            
            if auth_header:
                print(f"[OK] Authorization (Access Token): {auth_header[:50]}...")
            elif remapped_auth:
                print(f"[OK] x-amzn-Remapped-Authorization (Access Token): {remapped_auth[:50]}...")
            else:
                print(f"[WARN] Authorization/x-amzn-Remapped-Authorization header not found")
            
            if id_token_header:
                print(f"[OK] X-ID-Token (ID Token): {id_token_header[:50]}...")
            else:
                print(f"[WARN] X-ID-Token header not found")
            
            if refresh_token_header:
                print(f"[OK] X-Refresh-Token (Refresh Token): {refresh_token_header[:50]}...")
            else:
                print(f"[WARN] X-Refresh-Token header not found")
            
            if expires_in_header:
                print(f"[OK] X-Expires-In: {expires_in_header} seconds")
            else:
                print(f"[WARN] X-Expires-In header not found")
            
            return True
        else:
            print(f"\n[FAIL] Login failed with status code {response.status_code}")
            return False
    
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Test API Gateway Login Endpoint')
    parser.add_argument('--api-endpoint', required=True, help='API Gateway endpoint URL')
    parser.add_argument('--username', default='testuser', help='Username to login with')
    parser.add_argument('--password', default='TempPass123!@#', help='Password for login')
    
    args = parser.parse_args()
    
    result = test_login(args.api_endpoint, args.username, args.password)
    
    return 0 if result else 1


if __name__ == '__main__':
    sys.exit(main())
