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
    Lambda function to handle token refresh using Cognito AdminInitiateAuth
    Returns tokens in response headers
    """
    try:
        logger.info("=== Refresh Token Lambda Triggered ===")
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
            refresh_token = request_data.get('RefreshToken')
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
        
        if not refresh_token:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Bad Request',
                    'message': 'RefreshToken is required'
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
        
        logger.info("Attempting token refresh")
        
        try:
            response = cognito_client.admin_initiate_auth(
                UserPoolId=user_pool_id,
                ClientId=client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            
            auth_result = response.get('AuthenticationResult', {})
            id_token = auth_result.get('IdToken')
            access_token = auth_result.get('AccessToken')
            expires_in = auth_result.get('ExpiresIn')
            
            logger.info("Token refresh successful")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Authorization': access_token,
                    'X-ID-Token': id_token,
                    'X-Expires-In': str(expires_in)
                },
                'body': json.dumps({
                    'message': 'Token refresh successful'
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
                        'message': 'Invalid or expired refresh token'
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
                        'message': 'Token refresh failed'
                    })
                }
    
    except Exception as e:
        logger.error(f"Unexpected error in refresh token lambda: {str(e)}")
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
