"""
Revoke Token Lambda Function

This function handles token revocation for admin users only.
Revokes all tokens for a specified user.
"""

import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
cognito_client = boto3.client('cognito-idp')


def lambda_handler(event, context):
    """
    Lambda function to revoke tokens for a user (admin only)
    """
    try:
        logger.info("=== Revoke Token Lambda Triggered ===")
        logger.info(f"Event: {json.dumps(event)}")
        
        # Get authorizer context
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        user_role = authorizer.get('custom:role', 'unknown')
        admin_username = authorizer.get('claims', {}).get('cognito:username', 'unknown') if isinstance(authorizer.get('claims'), dict) else 'unknown'
        
        # Check if user is admin
        if user_role != 'admin':
            return error_response(403, f"User role '{user_role}' is not authorized for this operation")
        
        # Parse request body
        body = event.get('body')
        if not body:
            return error_response(400, 'Request body is required')
        
        try:
            request_data = json.loads(body)
            target_username = request_data.get('username')
        except json.JSONDecodeError:
            return error_response(400, 'Invalid JSON in request body')
        
        if not target_username:
            return error_response(400, 'Username is required in request body')
        
        # Get user pool ID from environment or ARN
        user_pool_id = os.environ.get('USER_POOL_ID', '')
        if not user_pool_id:
            logger.error("USER_POOL_ID environment variable not set")
            return error_response(500, 'Configuration error: USER_POOL_ID not set')
        
        # Revoke all tokens for the user
        try:
            cognito_client.admin_user_global_sign_out(
                UserPoolId=user_pool_id,
                Username=target_username
            )
            
            logger.info(f"Admin {admin_username} revoked all tokens for user {target_username}")
            
            return success_response({
                "message": f"Tokens revoked for user {target_username}",
                "admin": admin_username,
                "target_user": target_username,
                "status": "success"
            })
        
        except cognito_client.exceptions.UserNotFoundException:
            return error_response(404, f"User '{target_username}' not found")
        except ClientError as e:
            logger.error(f"Cognito error: {str(e)}")
            return error_response(500, f"Error revoking tokens: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return error_response(500, f"Internal server error: {str(e)}")


def success_response(data, status_code=200):
    """Return success response"""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(data)
    }


def error_response(status_code, message):
    """Return error response"""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "error": "Error",
            "message": message
        })
    }


import os
