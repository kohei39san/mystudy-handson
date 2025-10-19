#!/usr/bin/env python3
"""
Test script for API Gateway + Cognito + Lambda payload verification system

This script helps test the deployed infrastructure by:
1. Authenticating with Cognito User Pool
2. Making API calls to the deployed API Gateway
3. Verifying that Lambda logs the payloads correctly

Usage:
    python test-api.py --user-pool-id <pool_id> --client-id <client_id> --api-url <api_url> --username <email> --password <password>
"""

import argparse
import json
import requests
import boto3
from botocore.exceptions import ClientError
import time

class CognitoApiTester:
    def __init__(self, user_pool_id, client_id, api_url, region='ap-northeast-1'):
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.api_url = api_url.rstrip('/')
        self.region = region
        self.cognito_client = boto3.client('cognito-idp', region_name=region)
        self.access_token = None
        
    def authenticate(self, username, password):
        """Authenticate with Cognito User Pool and get access token"""
        try:
            print(f"Authenticating user: {username}")
            
            # Try different authentication flows
            try:
                # First try ADMIN_USER_PASSWORD_AUTH
                response = self.cognito_client.admin_initiate_auth(
                    UserPoolId=self.user_pool_id,
                    ClientId=self.client_id,
                    AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                    AuthParameters={
                        'USERNAME': username,
                        'PASSWORD': password
                    }
                )
            except ClientError as e1:
                print(f"ADMIN_USER_PASSWORD_AUTH failed: {e1}")
                try:
                    # Try ADMIN_NO_SRP_AUTH
                    response = self.cognito_client.admin_initiate_auth(
                        UserPoolId=self.user_pool_id,
                        ClientId=self.client_id,
                        AuthFlow='ADMIN_NO_SRP_AUTH',
                        AuthParameters={
                            'USERNAME': username,
                            'PASSWORD': password
                        }
                    )
                except ClientError as e2:
                    print(f"ADMIN_NO_SRP_AUTH also failed: {e2}")
                    raise e2
            
            # Handle challenge if needed (e.g., NEW_PASSWORD_REQUIRED)
            if 'ChallengeName' in response:
                print(f"Challenge required: {response['ChallengeName']}")
                if response['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                    print("New password required. Please set a permanent password first.")
                    return False
            
            # Extract tokens - use ID Token for API Gateway
            auth_result = response['AuthenticationResult']
            access_token = auth_result['AccessToken']
            self.access_token = auth_result['IdToken']  # Use ID Token for API Gateway
            
            print("Authentication successful!")
            print(f"ID Token (first 50 chars): {self.access_token[:50]}...")
            
            return True
            
        except ClientError as e:
            print(f"Authentication failed: {e}")
            return False
    
    def test_api_call(self, method='GET', path='/', data=None, headers=None):
        """Make an API call to the deployed API Gateway"""
        if not self.access_token:
            print("No access token available. Please authenticate first.")
            return None
        
        url = f"{self.api_url}{path}"
        
        # Prepare headers
        api_headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        if headers:
            api_headers.update(headers)
        
        try:
            print(f"\nMaking {method} request to: {url}")
            print(f"Headers: {json.dumps({k: v[:50] + '...' if len(v) > 50 else v for k, v in api_headers.items()}, indent=2)}")
            
            if data:
                print(f"Request body: {json.dumps(data, indent=2)}")
            
            # Make the request
            response = requests.request(
                method=method,
                url=url,
                headers=api_headers,
                json=data,
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            try:
                response_json = response.json()
                print(f"Response Body: {json.dumps(response_json, indent=2)}")
            except:
                print(f"Response Body (text): {response.text}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"API call failed: {e}")
            return None
    
    def run_test_suite(self):
        """Run a comprehensive test suite"""
        print("\nRunning API Test Suite")
        print("=" * 50)
        
        # Test 1: Simple GET request
        print("\nTest 1: Simple GET request")
        self.test_api_call('GET', '/')
        
        # Test 2: GET with query parameters
        print("\nTest 2: GET with query parameters")
        self.test_api_call('GET', '/?param1=value1&param2=value2')
        
        # Test 3: POST with JSON data
        print("\nTest 3: POST with JSON data")
        test_data = {
            'message': 'Hello from test script',
            'timestamp': time.time(),
            'test_id': 'test-001'
        }
        self.test_api_call('POST', '/test', data=test_data)
        
        # Test 4: PUT request
        print("\nTest 4: PUT request")
        update_data = {
            'action': 'update',
            'resource_id': '12345',
            'changes': ['field1', 'field2']
        }
        self.test_api_call('PUT', '/resource/12345', data=update_data)
        
        # Test 5: Custom headers
        print("\nTest 5: Request with custom headers")
        custom_headers = {
            'X-Custom-Header': 'test-value',
            'X-Request-ID': 'req-12345'
        }
        self.test_api_call('GET', '/custom', headers=custom_headers)
        
        print("\nTest suite completed!")
        print("\nCheck CloudWatch Logs for the Lambda function to see the logged payloads.")

def main():
    parser = argparse.ArgumentParser(description='Test API Gateway + Cognito + Lambda system')
    parser.add_argument('--user-pool-id', required=True, help='Cognito User Pool ID')
    parser.add_argument('--client-id', required=True, help='Cognito User Pool Client ID')
    parser.add_argument('--api-url', required=True, help='API Gateway URL')
    parser.add_argument('--username', required=True, help='Cognito username (email)')
    parser.add_argument('--password', required=True, help='Cognito user password')
    parser.add_argument('--region', default='ap-northeast-1', help='AWS region')
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = CognitoApiTester(
        user_pool_id=args.user_pool_id,
        client_id=args.client_id,
        api_url=args.api_url,
        region=args.region
    )
    
    # Authenticate
    if tester.authenticate(args.username, args.password):
        # Run test suite
        tester.run_test_suite()
    else:
        print("Authentication failed. Cannot proceed with API tests.")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())