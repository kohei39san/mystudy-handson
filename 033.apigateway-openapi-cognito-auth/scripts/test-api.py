#!/usr/bin/env python3
"""
API Gateway OpenAPI Cognito Auth Test Script

This script tests the deployed API endpoints with different user roles
and demonstrates query parameter functionality.
"""

import json
import requests
import boto3
import argparse
import sys
from typing import Dict, Optional
import time

class APITester:
    def __init__(self, api_endpoint: str, user_pool_id: str, client_id: str, region: str = 'ap-northeast-1'):
        self.api_endpoint = api_endpoint.rstrip('/')
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.region = region
        self.cognito_client = boto3.client('cognito-idp', region_name=region)
        
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return access token"""
        try:
            response = self.cognito_client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            if 'AuthenticationResult' in response:
                return response['AuthenticationResult']['AccessToken']
            else:
                print(f"❌ Authentication failed for {username}")
                return None
                
        except Exception as e:
            print(f"❌ Authentication error for {username}: {str(e)}")
            return None
    
    def make_request(self, method: str, endpoint: str, token: Optional[str] = None, 
                    params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to API endpoint"""
        url = f"{self.api_endpoint}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, params=params, json=json_data, timeout=30)
            else:
                return {'error': f'Unsupported method: {method}'}
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.text,
                'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            }
            
        except requests.exceptions.RequestException as e:
            return {'error': f'Request failed: {str(e)}'}
        except json.JSONDecodeError:
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.text,
                'json': None
            }
    
    def test_health_endpoint(self):
        """Test health endpoint (no authentication required)"""
        print("\n🔍 Testing /health endpoint (no authentication)")
        print("-" * 50)
        
        result = self.make_request('GET', '/health')
        
        if 'error' in result:
            print(f"❌ Request failed: {result['error']}")
            return False
        
        print(f"Status Code: {result['status_code']}")
        if result['json']:
            print(f"Response: {json.dumps(result['json'], indent=2)}")
        else:
            print(f"Response: {result['body']}")
        
        return result['status_code'] == 200
    
    def test_public_endpoint(self, token: str, user_type: str):
        """Test public endpoint with query parameters"""
        print(f"\n🔍 Testing /public endpoint as {user_type}")
        print("-" * 50)
        
        # Test with different query parameters
        test_cases = [
            {'format': 'json', 'include_metadata': 'true'},
            {'format': 'xml', 'include_metadata': 'false'},
            {'format': 'csv'},
            {}  # No parameters
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {params}")
            result = self.make_request('GET', '/public', token=token, params=params)
            
            if 'error' in result:
                print(f"❌ Request failed: {result['error']}")
                continue
            
            print(f"Status Code: {result['status_code']}")
            if result['json']:
                print(f"Query Parameters Received: {result['json'].get('query_parameters_received', {})}")
                if 'metadata' in result['json']:
                    print("✓ Metadata included in response")
            
            if result['status_code'] != 200:
                print(f"❌ Expected 200, got {result['status_code']}")
    
    def test_user_endpoint(self, token: str, user_type: str):
        """Test user endpoint with query parameters"""
        print(f"\n🔍 Testing /user endpoint as {user_type}")
        print("-" * 50)
        
        # Test with different query parameters
        test_cases = [
            {'filter': 'item', 'limit': '5', 'offset': '0'},
            {'limit': '3', 'offset': '10'},
            {'filter': 'test'},
            {}  # No parameters
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {params}")
            result = self.make_request('GET', '/user', token=token, params=params)
            
            if 'error' in result:
                print(f"❌ Request failed: {result['error']}")
                continue
            
            print(f"Status Code: {result['status_code']}")
            if result['json']:
                print(f"Query Parameters Received: {result['json'].get('query_parameters_received', {})}")
                pagination = result['json'].get('pagination', {})
                print(f"Pagination: limit={pagination.get('limit')}, offset={pagination.get('offset')}")
                print(f"Data items returned: {len(result['json'].get('data', []))}")
            
            if result['status_code'] not in [200, 403]:
                print(f"❌ Unexpected status code: {result['status_code']}")
    
    def test_admin_endpoint(self, token: str, user_type: str):
        """Test admin endpoint with query parameters and request body"""
        print(f"\n🔍 Testing /admin endpoint as {user_type}")
        print("-" * 50)
        
        # Test with different query parameters and request bodies
        test_cases = [
            {
                'params': {'action': 'create', 'target': 'user', 'priority': '8'},
                'body': {
                    'data': {'name': 'John Doe', 'email': 'john@example.com'},
                    'metadata': {'source': 'api_test', 'timestamp': '2024-01-01T00:00:00Z'}
                }
            },
            {
                'params': {'action': 'update', 'target': 'system'},
                'body': {
                    'data': {'config': 'updated_value'},
                    'metadata': {'version': '1.2.0'}
                }
            },
            {
                'params': {'action': 'delete'},
                'body': {
                    'data': {'id': '12345'}
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}: {test_case['params']}")
            result = self.make_request('POST', '/admin', token=token, 
                                     params=test_case['params'], json_data=test_case['body'])
            
            if 'error' in result:
                print(f"❌ Request failed: {result['error']}")
                continue
            
            print(f"Status Code: {result['status_code']}")
            if result['json']:
                print(f"Query Parameters Received: {result['json'].get('query_parameters_received', {})}")
                if 'result' in result['json']:
                    admin_result = result['json']['result']
                    print(f"Action: {admin_result.get('action')}")
                    print(f"Target: {admin_result.get('target')}")
                    print(f"Priority: {admin_result.get('priority')}")
            
            if result['status_code'] not in [200, 403]:
                print(f"❌ Unexpected status code: {result['status_code']}")
    
    def run_comprehensive_test(self, user_email: str, user_password: str, 
                             admin_email: str, admin_password: str):
        """Run comprehensive test suite"""
        print("🚀 Starting API Gateway OpenAPI Cognito Auth Test Suite")
        print("=" * 60)
        
        # Test health endpoint (no auth required)
        health_ok = self.test_health_endpoint()
        
        # Authenticate users
        print("\n🔐 Authenticating users...")
        user_token = self.authenticate_user(user_email, user_password)
        admin_token = self.authenticate_user(admin_email, admin_password)
        
        if not user_token:
            print(f"❌ Failed to authenticate regular user: {user_email}")
        else:
            print(f"✅ Regular user authenticated: {user_email}")
        
        if not admin_token:
            print(f"❌ Failed to authenticate admin user: {admin_email}")
        else:
            print(f"✅ Admin user authenticated: {admin_email}")
        
        # Test endpoints with different user roles
        if user_token:
            self.test_public_endpoint(user_token, "regular user")
            self.test_user_endpoint(user_token, "regular user")
            self.test_admin_endpoint(user_token, "regular user")  # Should fail
        
        if admin_token:
            self.test_public_endpoint(admin_token, "admin user")
            self.test_user_endpoint(admin_token, "admin user")
            self.test_admin_endpoint(admin_token, "admin user")
        
        # Test without authentication
        print(f"\n🔍 Testing endpoints without authentication")
        print("-" * 50)
        
        endpoints = ['/public', '/user', '/admin']
        for endpoint in endpoints:
            result = self.make_request('GET', endpoint)
            print(f"{endpoint}: Status {result.get('status_code', 'ERROR')} (Expected 401)")
        
        print("\n✅ Test suite completed!")

def main():
    parser = argparse.ArgumentParser(description='Test API Gateway OpenAPI Cognito Auth endpoints')
    parser.add_argument('--api-endpoint', required=True, help='API Gateway endpoint URL')
    parser.add_argument('--user-pool-id', required=True, help='Cognito User Pool ID')
    parser.add_argument('--client-id', required=True, help='Cognito User Pool Client ID')
    parser.add_argument('--user-email', default='test@example.com', help='Regular user email')
    parser.add_argument('--user-password', default='TempPass123!', help='Regular user password')
    parser.add_argument('--admin-email', default='admin@example.com', help='Admin user email')
    parser.add_argument('--admin-password', default='AdminPass123!', help='Admin user password')
    parser.add_argument('--region', default='ap-northeast-1', help='AWS region')
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = APITester(
        api_endpoint=args.api_endpoint,
        user_pool_id=args.user_pool_id,
        client_id=args.client_id,
        region=args.region
    )
    
    # Run tests
    try:
        tester.run_comprehensive_test(
            user_email=args.user_email,
            user_password=args.user_password,
            admin_email=args.admin_email,
            admin_password=args.admin_password
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()