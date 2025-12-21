import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import json


@pytest.fixture
def mock_context():
    """Mock Lambda context object"""
    context = Mock()
    context.aws_request_id = 'test-request-id-123'
    context.function_name = 'test-function'
    context.function_version = '1'
    context.invoked_function_arn = 'arn:aws:lambda:ap-northeast-1:123456789012:function:test-function'
    context.memory_limit_in_mb = 256
    context.remaining_time_in_millis = 30000
    return context


@pytest.fixture
def mock_environment(monkeypatch):
    """Mock environment variables"""
    monkeypatch.setenv('AURORA_SECRET_ARN', 'arn:aws:secretsmanager:ap-northeast-1:123456789012:secret:test-secret')
    monkeypatch.setenv('API_URL', 'http://test-api.example.com')
    monkeypatch.setenv('AWS_REGION', 'ap-northeast-1')


@pytest.fixture
def mock_secrets_response():
    """Mock Secrets Manager response"""
    return {
        'SecretString': json.dumps({
            'engine': 'postgres',
            'host': 'test-aurora-cluster.cluster-xyz.ap-northeast-1.rds.amazonaws.com',
            'port': 5432,
            'dbname': 'testdb',
            'username': 'postgres'
        })
    }


@pytest.fixture
def mock_db_connection():
    """Mock database connection and cursor"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Mock cursor methods
    mock_cursor.fetchone.side_effect = [
        ('PostgreSQL 15.4 on x86_64-pc-linux-gnu',),  # version query
        ('testdb', 'iam_user', '10.0.1.100', 5432)    # connection info query
    ]
    
    mock_conn.cursor.return_value = mock_cursor
    
    return mock_conn, mock_cursor


@pytest.fixture
def mock_api_responses():
    """Mock API responses"""
    health_response = Mock()
    health_response.json.return_value = {'status': 'healthy', 'service': 'flask-api'}
    health_response.raise_for_status.return_value = None
    
    data_response = Mock()
    data_response.json.return_value = {
        'data': [
            {'id': 1, 'name': 'Sample Data 1'},
            {'id': 2, 'name': 'Sample Data 2'}
        ],
        'total': 2
    }
    data_response.raise_for_status.return_value = None
    
    create_response = Mock()
    create_response.json.return_value = {
        'id': 3,
        'name': 'Lambda Created Data',
        'status': 'created'
    }
    create_response.raise_for_status.return_value = None
    
    return health_response, data_response, create_response