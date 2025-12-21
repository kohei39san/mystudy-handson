import json
import boto3
import psycopg2
import requests
import os
from typing import Dict, Any, Optional


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function to process data from Aurora, Secrets Manager, and ECS
    
    This function demonstrates:
    - Retrieving database connection info from Secrets Manager
    - Connecting to Aurora PostgreSQL with IAM token authentication
    - Making HTTP requests to ECS-hosted Flask API
    - Combining and returning processed data
    """
    try:
        # Initialize AWS clients
        secrets_client = boto3.client('secretsmanager')
        rds_client = boto3.client('rds')
        
        # Get database connection info from Secrets Manager
        db_config = get_database_config(secrets_client)
        
        # Connect to Aurora and fetch data
        db_data = fetch_database_data(db_config, rds_client)
        
        # Call ECS API
        api_data = fetch_api_data()
        
        # Process and return combined data
        result = {
            'statusCode': 200,
            'body': json.dumps({
                'database_data': db_data,
                'api_data': api_data,
                'processed_at': context.aws_request_id,
                'function_name': context.function_name
            })
        }
        
        return result
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'request_id': context.aws_request_id
            })
        }


def get_database_config(secrets_client: boto3.client) -> Dict[str, str]:
    """
    Get database configuration from Secrets Manager
    
    Args:
        secrets_client: Boto3 Secrets Manager client
        
    Returns:
        Dictionary containing database connection parameters
    """
    secret_arn = os.environ['AURORA_SECRET_ARN']
    
    response = secrets_client.get_secret_value(SecretId=secret_arn)
    secret_data = json.loads(response['SecretString'])
    
    return secret_data


def fetch_database_data(db_config: Dict[str, str], rds_client: boto3.client) -> Optional[Dict[str, Any]]:
    """
    Fetch data from Aurora PostgreSQL using IAM token authentication
    
    Args:
        db_config: Database connection configuration
        rds_client: Boto3 RDS client
        
    Returns:
        Dictionary containing database query results or error information
    """
    try:
        # Generate IAM token for authentication
        token = rds_client.generate_db_auth_token(
            DBHostname=db_config['host'],
            Port=db_config['port'],
            DBUsername='iam_user'
        )
        
        # Connect to database
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['dbname'],
            user='iam_user',
            password=token,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Execute sample queries
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        cursor.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
        connection_info = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            'connection_status': 'success',
            'database_version': version[0] if version else None,
            'database_name': connection_info[0] if connection_info else None,
            'current_user': connection_info[1] if connection_info else None,
            'server_address': connection_info[2] if connection_info else None,
            'server_port': connection_info[3] if connection_info else None
        }
        
    except Exception as e:
        return {
            'connection_status': 'failed',
            'error': str(e)
        }


def fetch_api_data() -> Optional[Dict[str, Any]]:
    """
    Fetch data from ECS Flask API
    
    Returns:
        Dictionary containing API response data or error information
    """
    try:
        api_url = os.environ['API_URL']
        
        # Health check
        health_response = requests.get(f"{api_url}/health", timeout=10)
        health_response.raise_for_status()
        health_data = health_response.json()
        
        # Get data
        data_response = requests.get(f"{api_url}/api/data", timeout=10)
        data_response.raise_for_status()
        api_data = data_response.json()
        
        # Create new data
        create_response = requests.post(
            f"{api_url}/api/data",
            json={'name': 'Lambda Created Data'},
            timeout=10
        )
        create_response.raise_for_status()
        create_data = create_response.json()
        
        return {
            'api_status': 'success',
            'health_check': health_data,
            'existing_data': api_data,
            'created_data': create_data
        }
        
    except Exception as e:
        return {
            'api_status': 'failed',
            'error': str(e)
        }