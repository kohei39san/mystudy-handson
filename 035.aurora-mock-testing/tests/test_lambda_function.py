import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import urllib.error
from moto import mock_aws
import boto3

# Import the lambda function
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)
from scripts.lambda_function import (
    lambda_handler,
    get_database_config,
    fetch_database_data,
    fetch_api_data
)


class TestLambdaHandler:
    """Test cases for the main lambda_handler function"""
    
    @patch('lambda_function.urllib.request')
    @patch('lambda_function.psycopg2')
    @patch('lambda_function.boto3')
    def test_lambda_handler_success(
        self, 
        mock_boto3, 
        mock_psycopg2, 
        mock_urllib,
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
        # Mock urllib responses
        health_response = Mock()
        health_response.read.return_value = json.dumps({'status': 'healthy', 'service': 'flask-api'}).encode('utf-8')
        health_response.__enter__ = Mock(return_value=health_response)
        health_response.__exit__ = Mock(return_value=None)
        data_response = Mock()
        data_response.json.return_value = {
            'total': 1
        }
        data_response.read.return_value = json.dumps({
            'total': 1
        }).encode('utf-8')
        data_response.__enter__ = Mock(return_value=data_response)
        data_response.__exit__ = Mock(return_value=None)
        create_response = Mock()
        create_response.json.return_value = {
            'name': 'Lambda Created Data',
            'status': 'created'
        }
        create_response.read.return_value = json.dumps({
            'name': 'Lambda Created Data',
            'status': 'created'
        }).encode('utf-8')
        create_response.__enter__ = Mock(return_value=create_response)
        create_response.__exit__ = Mock(return_value=None)
        mock_requests.get.side_effect = [health_response, data_response]
        mock_urllib.urlopen.side_effect = [health_response, data_response, create_response]
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

    @patch('lambda_function.urllib.request')
    @patch('lambda_function.psycopg2')
    @patch('lambda_function.boto3')
    def test_lambda_handler_secrets_manager_error(
        self, 
        mock_boto3, 
        mock_psycopg2, 
        mock_urllib,
        mock_context,
        mock_environment
    ):
        """Test lambda handler with Secrets Manager error"""
        # Setup mocks
        mock_secrets_client = MagicMock()
        mock_rds_client = MagicMock()
        mock_boto3.client.side_effect = [mock_secrets_client, mock_rds_client]
        
        # Make secrets manager throw an exception
        mock_secrets_client.get_secret_value.side_effect = Exception("Secrets Manager error")
        
        # Execute
        event = {'test': 'data'}
        result = lambda_handler(event, mock_context)
        
        # Assertions
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'error' in body
        assert 'Secrets Manager error' in body['error']
        assert body['request_id'] == 'test-request-id-123'

    @patch('lambda_function.urllib.request')
    @patch('lambda_function.psycopg2')
    @patch('lambda_function.boto3')
    def test_lambda_handler_database_error(
        self, 
        mock_boto3, 
        mock_psycopg2, 
        mock_urllib,
        mock_context,
        mock_environment,
        mock_secrets_response
    ):
        """Test lambda handler with database connection error"""
        # Setup mocks
        mock_secrets_client = MagicMock()
        mock_rds_client = MagicMock()
        mock_boto3.client.side_effect = [mock_secrets_client, mock_rds_client]
        
        mock_secrets_client.get_secret_value.return_value = mock_secrets_response
        mock_rds_client.generate_db_auth_token.return_value = 'mock-iam-token'
        
        # Make database connection throw an exception
        mock_psycopg2.connect.side_effect = Exception("Database connection failed")
        
        # Mock successful API responses
        health_response = Mock()
        health_response.read.return_value = json.dumps({'status': 'healthy', 'service': 'flask-api'}).encode('utf-8')
        health_response.__enter__ = Mock(return_value=health_response)
        health_response.__exit__ = Mock(return_value=None)
        
        data_response = Mock()
        data_response.read.return_value = json.dumps({
            'data': [{'id': 1, 'name': 'Sample Data 1'}],
            'total': 1
        }).encode('utf-8')
        data_response.__enter__ = Mock(return_value=data_response)
        data_response.__exit__ = Mock(return_value=None)
        
        create_response = Mock()
        create_response.read.return_value = json.dumps({
            'id': 3,
            'name': 'Lambda Created Data',
            'status': 'created'
        }).encode('utf-8')
        create_response.__enter__ = Mock(return_value=create_response)
        create_response.__exit__ = Mock(return_value=None)
        
        mock_urllib.urlopen.side_effect = [health_response, data_response, create_response]
        
        # Execute
        event = {'test': 'data'}
        result = lambda_handler(event, mock_context)
        
        # Assertions
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert 'database_data' in body
        assert body['database_data']['connection_status'] == 'failed'
        assert 'Database connection failed' in body['database_data']['error']


class TestGetDatabaseConfig:
    """Test cases for get_database_config function"""
    
    def test_get_database_config_success(self, mock_environment, mock_secrets_response):
        """Test successful database config retrieval"""
        mock_secrets_client = MagicMock()
        mock_secrets_client.get_secret_value.return_value = mock_secrets_response
        
        result = get_database_config(mock_secrets_client)
        
        expected = {
            'engine': 'postgres',
            'host': 'test-aurora-cluster.cluster-xyz.ap-northeast-1.rds.amazonaws.com',
            'port': 5432,
            'dbname': 'testdb',
            'username': 'postgres'
        }
        assert result == expected
        mock_secrets_client.get_secret_value.assert_called_once_with(
            SecretId='arn:aws:secretsmanager:ap-northeast-1:123456789012:secret:test-secret'
        )

    def test_get_database_config_error(self, mock_environment):
        """Test database config retrieval with error"""
        mock_secrets_client = MagicMock()
        mock_secrets_client.get_secret_value.side_effect = Exception("Access denied")
        
        with pytest.raises(Exception) as exc_info:
            get_database_config(mock_secrets_client)
        
        assert "Access denied" in str(exc_info.value)


class TestFetchDatabaseData:
    """Test cases for fetch_database_data function"""
    
    @patch('lambda_function.psycopg2')
    def test_fetch_database_data_success(self, mock_psycopg2):
        """Test successful database data fetch"""
        # Setup mocks
        mock_rds_client = MagicMock()
        mock_rds_client.generate_db_auth_token.return_value = 'mock-iam-token'
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            ('PostgreSQL 15.4 on x86_64-pc-linux-gnu',),
            ('testdb', 'iam_user', '10.0.1.100', 5432)
        ]
        mock_conn.cursor.return_value = mock_cursor
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
        
        # Verify token generation
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
        
        # Make connection fail
        mock_psycopg2.connect.side_effect = Exception("Connection failed")
        
        db_config = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'testdb'
        }
        
        result = fetch_database_data(db_config, mock_rds_client)
        
        assert result['connection_status'] == 'failed'
        assert 'Connection failed' in result['error']

    @patch('lambda_function.psycopg2')
    def test_fetch_database_data_query_error(self, mock_psycopg2):
        """Test database data fetch with query error"""
        mock_rds_client = MagicMock()
        mock_rds_client.generate_db_auth_token.return_value = 'mock-iam-token'
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn
        
        db_config = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'testdb'
        }
        
        result = fetch_database_data(db_config, mock_rds_client)
        
        assert result['connection_status'] == 'failed'
        assert 'Query failed' in result['error']


class TestFetchApiData:
    """Test cases for fetch_api_data function"""
    
    @patch('lambda_function.urllib.request')
    def test_fetch_api_data_success(self, mock_urllib, mock_environment):
        """Test successful API data fetch"""
        # Mock urllib responses
        health_response = Mock()
        health_response.read.return_value = json.dumps({'status': 'healthy', 'service': 'flask-api'}).encode('utf-8')
        health_response.__enter__ = Mock(return_value=health_response)
        health_response.__exit__ = Mock(return_value=None)
        
        data_response = Mock()
        data_response.read.return_value = json.dumps({
            'data': [{'id': 1, 'name': 'Sample Data 1'}],
            'total': 1
        }).encode('utf-8')
        data_response.__enter__ = Mock(return_value=data_response)
        data_response.__exit__ = Mock(return_value=None)
        
        create_response = Mock()
        create_response.read.return_value = json.dumps({
            'id': 3,
            'name': 'Lambda Created Data',
            'status': 'created'
        }).encode('utf-8')
        create_response.__enter__ = Mock(return_value=create_response)
        create_response.__exit__ = Mock(return_value=None)
        
        mock_urllib.urlopen.side_effect = [health_response, data_response, create_response]
        
        result = fetch_api_data()
        
        assert result['api_status'] == 'success'
        assert result['health_check']['status'] == 'healthy'
        assert result['existing_data']['total'] == 1
        assert result['created_data']['name'] == 'Lambda Created Data'
        
        # Verify urllib calls
        assert mock_urllib.urlopen.call_count == 3
        assert mock_urllib.Request.call_count == 3

    @patch('lambda_function.urllib.request')
    def test_fetch_api_data_http_error(self, mock_urllib, mock_environment):
        """Test API data fetch with HTTP error"""
        # Make urllib throw HTTPError
        http_error = urllib.error.HTTPError(
            url='http://test-api.example.com/health',
            code=404,
            msg='Not Found',
            hdrs={},
            fp=None
        )
        mock_urllib.urlopen.side_effect = http_error
        
        result = fetch_api_data()
        
        assert result['api_status'] == 'failed'
        assert result['error_type'] == 'HTTPError'
        assert 'HTTP Error 404' in result['error']

    @patch('lambda_function.urllib.request')
    def test_fetch_api_data_url_error(self, mock_urllib, mock_environment):
        """Test API data fetch with URL error"""
        # Make urllib throw URLError
        url_error = urllib.error.URLError('Connection refused')
        mock_urllib.urlopen.side_effect = url_error
        
        result = fetch_api_data()
        
        assert result['api_status'] == 'failed'
        assert result['error_type'] == 'URLError'
        assert 'Connection refused' in result['error']

    @patch('lambda_function.urllib.request')
    def test_fetch_api_data_general_error(self, mock_urllib, mock_environment):
        """Test API data fetch with general error"""
        # Make urllib throw general exception
        mock_urllib.urlopen.side_effect = Exception("Unexpected error")
        
        result = fetch_api_data()
        
        assert result['api_status'] == 'failed'
        assert result['error_type'] == 'GeneralError'
        assert 'Unexpected error' in result['error']


class TestMotoIntegration:
    """Integration tests using moto for AWS service mocking"""
    
    @mock_aws
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