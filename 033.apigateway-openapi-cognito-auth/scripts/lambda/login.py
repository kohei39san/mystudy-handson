import json
import logging
import boto3
import os
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
cognito_client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    """
    Lambda function to handle user login using Cognito AdminInitiateAuth
    Returns tokens in response headers
    """
    try:
        logger.info("=== Login Lambda Triggered ===")
        logger.info(f"Event path: {event.get('path', 'unknown')}")
        
        body = event.get('body')
        if not body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Bad Request',
                    'message': 'Request body is required'
                })
            }
        
        try:
            request_data = json.loads(body)
            username = request_data.get('username')
            password = request_data.get('password')
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Bad Request',
                    'message': 'Invalid JSON in request body'
                })
            }
        
        if not username or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Bad Request',
                    'message': 'Username and password are required'
                })
            }
        
        user_pool_id = os.environ.get('USER_POOL_ID')
        client_id = os.environ.get('CLIENT_ID')
        
        if not user_pool_id or not client_id:
            logger.error("Missing environment variables: USER_POOL_ID or CLIENT_ID")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Internal Server Error',
                    'message': 'Configuration error'
                })
            }
        
        logger.info(f"Attempting login for user: {username}")
        
        try:
            response = cognito_client.admin_initiate_auth(
                UserPoolId=user_pool_id,
                ClientId=client_id,
                AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            auth_result = response.get('AuthenticationResult', {})
            id_token = auth_result.get('IdToken')
            access_token = auth_result.get('AccessToken')
            refresh_token = auth_result.get('RefreshToken')
            expires_in = auth_result.get('ExpiresIn')
            
            logger.info(f"Login successful for user: {username}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Authorization': access_token,
                    'X-ID-Token': id_token,
                    'X-Refresh-Token': refresh_token,
                    'X-Expires-In': str(expires_in)
                },
                'body': json.dumps({
                    'message': 'Login successful'
                })
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Cognito error: {error_code} - {str(e)}")
            
            if error_code == 'NotAuthorizedException':
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Unauthorized',
                        'message': 'Invalid username or password'
                    })
                }
            elif error_code == 'UserNotFoundException':
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Not Found',
                        'message': 'User not found'
                    })
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Internal Server Error',
                        'message': 'Authentication failed'
                    })
                }
    
    except Exception as e:
        logger.error(f"Unexpected error in login lambda: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'request_id': context.aws_request_id
            })
        }
