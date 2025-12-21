import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from moto import mock_secretsmanager, mock_rds
import boto3

# Import the lambda function
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from lambda_function import (
    lambda_handler,
    get_database_config,
    fetch_database_data,
    fetch_api_data
)


class TestLambdaHandler:
    """Test cases for the main lambda_handler function"""
    
    @patch('lambda_function.requests')
    @patch('lambda_function.psycopg2')
    @patch('lambda_function.boto3')
    def test_lambda_handler_success(
        self, 
        mock_boto3, 
        mock_psycopg2, 
        mock_requests,
        mock_context,
        mock_environment,
        mock_secrets_response
    ):
        """Test successful lambda handler execution"""
        # Setup mocks
        mock_secrets_client = MagicMock()
        mock_rds_client = MagicMock()
        mock_boto3.client.side_effect = [mock_secrets_client, mock_rds_client]
        
        mock_secrets_client.get_secret_value.return_value = mock_secrets_response
        mock_rds_client.generate_db_auth_token.return_value = 'mock-iam-token'
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            ('PostgreSQL 15.4 on x86_64-pc-linux-gnu',),
            ('testdb', 'iam_user', '10.0.1.100', 5432)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn
        
        # Mock API responses
        health_response = Mock()
        health_response.json.return_value = {'status': 'healthy', 'service': 'flask-api'}
        health_response.raise_for_status.return_value = None
        
        data_response = Mock()
        data_response.json.return_value = {
            'data': [{'id': 1, 'name': 'Sample Data 1'}],
            'total': 1
        }
        data_response.raise_for_status.return_value = None
        
        create_response = Mock()
        create_response.json.return_value = {
            'id': 3,
            'name': 'Lambda Created Data',
            'status': 'created'
        }
        create_response.raise_for_status.return_value = None
        
        mock_requests.get.side_effect = [health_response, data_response]
        mock_requests.post.return_value = create_response
        
        # Execute
        event = {'test': 'data'}
        result = lambda_handler(event, mock_context)
        
        # Assertions
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert 'database_data' in body
        assert 'api_data' in body
        assert body['processed_at'] == 'test-request-id-123'
        assert body['function_name'] == 'test-function'


class TestMotoIntegration:
    """Integration tests using moto for AWS service mocking"""
    
    @mock_secretsmanager
    def test_secrets_manager_integration(self, mock_environment):
        """Test Secrets Manager integration with moto"""
        # Create mock secret
        secrets_client = boto3.client('secretsmanager', region_name='ap-northeast-1')
        secret_value = {
            'engine': 'postgres',
            'host': 'test-aurora-cluster.cluster-xyz.ap-northeast-1.rds.amazonaws.com',
            'port': 5432,
            'dbname': 'testdb',
            'username': 'postgres'
        }
        
        secrets_client.create_secret(
            Name='arn:aws:secretsmanager:ap-northeast-1:123456789012:secret:test-secret',
            SecretString=json.dumps(secret_value)
        )
        
        # Test function
        result = get_database_config(secrets_client)
        
        assert result == secret_value