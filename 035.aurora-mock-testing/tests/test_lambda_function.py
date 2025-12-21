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
    fetch_api_data,
    create_sample_table
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
        mock_secrets_response,
        mock_db_connection,
        mock_api_responses
    ):
        """Test successful lambda handler execution"""
        # Setup mocks
        mock_secrets_client = MagicMock()
        mock_rds_client = MagicMock()
        mock_boto3.client.side_effect = [mock_secrets_client, mock_rds_client]
        
        mock_secrets_client.get_secret_value.return_value = mock_secrets_response
        mock_rds_client.generate_db_auth_token.return_value = 'mock-iam-token'
        
        mock_conn, mock_cursor = mock_db_connection
        mock_psycopg2.connect.return_value = mock_conn
        
        health_response, data_response, create_response = mock_api_responses
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
        
        # Verify database data
        assert body['database_data']['connection_status'] == 'success'
        assert 'PostgreSQL 15.4' in body['database_data']['database_version']
        
        # Verify API data
        assert body['api_data']['api_status'] == 'success'
        assert body['api_data']['health_check']['status'] == 'healthy'
    
    @patch('lambda_function.boto3')
    def test_lambda_handler_error(self, mock_boto3, mock_context, mock_environment):
        """Test lambda handler with error"""
        # Setup mock to raise exception
        mock_boto3.client.side_effect = Exception('AWS service error')
        
        # Execute
        event = {'test': 'data'}
        result = lambda_handler(event, mock_context)
        
        # Assertions
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'error' in body
        assert body['request_id'] == 'test-request-id-123'


class TestGetDatabaseConfig:
    """Test cases for get_database_config function"""
    
    def test_get_database_config_success(self, mock_environment, mock_secrets_response):
        """Test successful database config retrieval"""
        mock_secrets_client = MagicMock()
        mock_secrets_client.get_secret_value.return_value = mock_secrets_response
        
        result = get_database_config(mock_secrets_client)
        
        assert result['engine'] == 'postgres'
        assert result['host'] == 'test-aurora-cluster.cluster-xyz.ap-northeast-1.rds.amazonaws.com'
        assert result['port'] == 5432
        assert result['dbname'] == 'testdb'
        assert result['username'] == 'postgres'
        
        mock_secrets_client.get_secret_value.assert_called_once_with(
            SecretId='arn:aws:secretsmanager:ap-northeast-1:123456789012:secret:test-secret'
        )
    
    def test_get_database_config_error(self, mock_environment):
        """Test database config retrieval with error"""
        mock_secrets_client = MagicMock()
        mock_secrets_client.get_secret_value.side_effect = Exception('Secret not found')
        
        with pytest.raises(Exception, match='Secret not found'):
            get_database_config(mock_secrets_client)


class TestFetchDatabaseData:
    """Test cases for fetch_database_data function"""
    
    @patch('lambda_function.psycopg2')
    def test_fetch_database_data_success(self, mock_psycopg2, mock_db_connection):
        """Test successful database data fetch"""
        mock_rds_client = MagicMock()
        mock_rds_client.generate_db_auth_token.return_value = 'mock-iam-token'
        
        mock_conn, mock_cursor = mock_db_connection
        mock_psycopg2.connect.return_value = mock_conn
        
        db_config = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'testdb'
        }
        
        result = fetch_database_data(db_config, mock_rds_client)
        
        assert result['connection_status'] == 'success'
        assert 'PostgreSQL 15.4' in result['database_version']
        assert result['database_name'] == 'testdb'
        assert result['current_user'] == 'iam_user'
        assert result['server_address'] == '10.0.1.100'
        assert result['server_port'] == 5432
        
        # Verify IAM token generation
        mock_rds_client.generate_db_auth_token.assert_called_once_with(
            DBHostname='test-host',
            Port=5432,
            DBUsername='iam_user'
        )
        
        # Verify database connection
        mock_psycopg2.connect.assert_called_once_with(
            host='test-host',
            port=5432,
            database='testdb',
            user='iam_user',
            password='mock-iam-token',
            sslmode='require'
        )
    
    @patch('lambda_function.psycopg2')
    def test_fetch_database_data_connection_error(self, mock_psycopg2):
        """Test database data fetch with connection error"""
        mock_rds_client = MagicMock()
        mock_rds_client.generate_db_auth_token.return_value = 'mock-iam-token'
        mock_psycopg2.connect.side_effect = Exception('Connection failed')
        
        db_config = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'testdb'
        }
        
        result = fetch_database_data(db_config, mock_rds_client)
        
        assert result['connection_status'] == 'failed'
        assert 'Connection failed' in result['error']
    
    @patch('lambda_function.psycopg2')
    def test_fetch_database_data_iam_token_error(self, mock_psycopg2):
        """Test database data fetch with IAM token generation error"""
        mock_rds_client = MagicMock()
        mock_rds_client.generate_db_auth_token.side_effect = Exception('IAM token generation failed')
        
        db_config = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'testdb'
        }
        
        result = fetch_database_data(db_config, mock_rds_client)
        
        assert result['connection_status'] == 'failed'
        assert 'IAM token generation failed' in result['error']


class TestFetchApiData:
    """Test cases for fetch_api_data function"""
    
    @patch('lambda_function.requests')
    def test_fetch_api_data_success(self, mock_requests, mock_environment, mock_api_responses):
        """Test successful API data fetch"""
        health_response, data_response, create_response = mock_api_responses
        mock_requests.get.side_effect = [health_response, data_response]
        mock_requests.post.return_value = create_response
        
        result = fetch_api_data()
        
        assert result['api_status'] == 'success'
        assert result['health_check']['status'] == 'healthy'
        assert len(result['existing_data']['data']) == 2
        assert result['created_data']['name'] == 'Lambda Created Data'
        
        # Verify API calls
        assert mock_requests.get.call_count == 2
        mock_requests.get.assert_any_call('http://test-api.example.com/health', timeout=10)
        mock_requests.get.assert_any_call('http://test-api.example.com/api/data', timeout=10)
        
        mock_requests.post.assert_called_once_with(
            'http://test-api.example.com/api/data',
            json={'name': 'Lambda Created Data'},
            timeout=10
        )
    
    @patch('lambda_function.requests')
    def test_fetch_api_data_error(self, mock_requests, mock_environment):
        """Test API data fetch with error"""
        mock_requests.get.side_effect = Exception('API connection failed')
        
        result = fetch_api_data()
        
        assert result['api_status'] == 'failed'
        assert 'API connection failed' in result['error']


class TestCreateSampleTable:
    """Test cases for create_sample_table function"""
    
    @patch('lambda_function.psycopg2')
    def test_create_sample_table_success(self, mock_psycopg2):
        """Test successful sample table creation"""
        mock_rds_client = MagicMock()
        mock_rds_client.generate_db_auth_token.return_value = 'mock-iam-token'
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn
        
        db_config = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'testdb'
        }
        
        result = create_sample_table(db_config, mock_rds_client)
        
        assert result['table_creation'] == 'success'
        assert 'Sample table created and populated' in result['message']
        
        # Verify table creation and data insertion
        assert mock_cursor.execute.call_count == 2
        mock_conn.commit.assert_called_once()
    
    @patch('lambda_function.psycopg2')
    def test_create_sample_table_error(self, mock_psycopg2):
        """Test sample table creation with error"""
        mock_rds_client = MagicMock()
        mock_rds_client.generate_db_auth_token.return_value = 'mock-iam-token'
        mock_psycopg2.connect.side_effect = Exception('Table creation failed')
        
        db_config = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'testdb'
        }
        
        result = create_sample_table(db_config, mock_rds_client)
        
        assert result['table_creation'] == 'failed'
        assert 'Table creation failed' in result['error']


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
    
    @mock_rds
    def test_rds_token_generation_integration(self):
        """Test RDS IAM token generation with moto"""
        rds_client = boto3.client('rds', region_name='ap-northeast-1')
        
        # Generate IAM token (moto will return a mock token)
        token = rds_client.generate_db_auth_token(
            DBHostname='test-host',
            Port=5432,
            DBUsername='iam_user'
        )
        
        assert token is not None
        assert isinstance(token, str)