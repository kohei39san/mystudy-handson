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