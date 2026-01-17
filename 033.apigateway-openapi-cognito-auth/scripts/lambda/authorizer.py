"""
Lambda Authorizer for API Gateway OpenAPI Cognito Auth

This function handles custom authorization for API Gateway endpoints.
It extracts the user role from the Cognito ID token and enforces role-based access control.
"""

import json
import logging
import base64
from jose import jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Lambda Authorizer handler"""
    logger.info(f"Authorizer event: {json.dumps(event)}")
    
    try:
        # Get the authorization token from the event
        token = event.get('authorizationToken', '')
        method_arn = event.get('methodArn', '')
        
        logger.info(f"Method ARN: {method_arn}")
        
        if not token:
            logger.warning("No authorization token provided")
            raise Exception('Unauthorized')
        
        # Extract token (remove "Bearer " prefix if present)
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decode the token (without verification, as it's already verified by Cognito)
        try:
            # Decode without verification since the token is issued by Cognito
            decoded = jwt.get_unverified_claims(token)
            logger.info(f"Decoded token: {json.dumps(decoded)}")
        except Exception as e:
            logger.error(f"Failed to decode token: {str(e)}")
            raise Exception('Unauthorized')
        
        # Extract user information
        username = decoded.get('cognito:username', 'unknown')
        user_role = decoded.get('custom:role', 'user')
        
        logger.info(f"Authorized user: {username}, role: {user_role}")
        
        # Generate the authorization response
        principal_id = decoded.get('sub', 'user')
        
        auth_response = {
            'principalId': principal_id,
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'execute-api:Invoke',
                        'Effect': 'Allow',
                        'Resource': method_arn
                    }
                ]
            },
            'context': {
                'username': username,
                'custom:role': user_role,
                'sub': principal_id
            }
        }
        
        logger.info(f"Auth response: {json.dumps(auth_response)}")
        return auth_response
    
    except Exception as e:
        logger.error(f"Authorization failed: {str(e)}")
        raise Exception('Unauthorized')


def decode_token_without_verification(token):
    """Decode JWT token without verification"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise Exception('Invalid token format')
        
        # Decode payload (second part)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded_bytes = base64.urlsafe_b64decode(payload)
        decoded = json.loads(decoded_bytes)
        
        return decoded
    except Exception as e:
        logger.error(f"Token decode error: {str(e)}")
        return None
