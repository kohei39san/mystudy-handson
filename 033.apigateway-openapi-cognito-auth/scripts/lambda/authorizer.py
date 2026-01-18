"""
Lambda Authorizer for API Gateway OpenAPI Cognito Auth

This function handles custom authorization for API Gateway endpoints.
It extracts the user role from the Cognito ID token and enforces role-based access control.
"""

import json
import logging
import os
import base64
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from jose import jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

POLICY_STORE_ID = os.environ.get("POLICY_STORE_ID", "")
PRINCIPAL_ENTITY_TYPE = os.environ.get("PRINCIPAL_ENTITY_TYPE", "User")
vp = boto3.client("verifiedpermissions")


def map_action(path: str, method: str) -> str:
    """Map HTTP path to Cedar action ID (path itself)."""
    normalized_path = path.rstrip('/') or '/'
    return f"{method.upper()} {normalized_path}"


def lambda_handler(event, context):
    """Lambda Authorizer handler"""
    logger.info(f"Authorizer event: {json.dumps(event)}")
    
    try:
        # For REQUEST type authorizer, get the token from headers
        headers = event.get('headers', {})
        auth_header = headers.get('authorization') or headers.get('Authorization', '')
        method_arn = event.get('methodArn', '')
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('httpMethod', '')
        path = event.get('path') or event.get('requestContext', {}).get('resourcePath', '')
        
        logger.info(f"Method ARN: {method_arn}")
        logger.info(f"Authorization header: {auth_header[:50] if auth_header else 'None'}...")
        
        if not auth_header:
            logger.warning("No authorization token provided")
            raise Exception('Unauthorized')
        
        token = auth_header
        
        # Extract token (remove "Bearer " prefix if present)
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decode the token (without verification, as it's already verified by Cognito)
        try:
            decoded = jwt.get_unverified_claims(token)
            logger.info(f"Decoded token: {json.dumps(decoded)}")
        except Exception as e:
            logger.error(f"Failed to decode token: {str(e)}")
            raise Exception('Unauthorized')
        
        # Extract user information
        username = decoded.get('cognito:username') or decoded.get('username', 'unknown')
        
        # Get user role from Cognito groups or custom:role
        # Check if custom:role already exists in token
        user_role = decoded.get('custom:role')
        if not user_role:
            # Fall back to cognito:groups
            groups = decoded.get('cognito:groups', [])
            if 'api-admins' in groups:
                user_role = 'admin'
            elif 'api-users' in groups:
                user_role = 'user'
            else:
                user_role = 'unknown'
        
        logger.info(f"User: {username}, role: {user_role}")

        if not POLICY_STORE_ID:
            logger.error("POLICY_STORE_ID not configured")
            raise Exception('Unauthorized')

        action_id = map_action(path, http_method)
        resource_id = f"{http_method.upper()} {path or '/'}"

        logger.info(f"Calling AVP: action={action_id}, resource={resource_id}, policyStore={POLICY_STORE_ID}")

        try:
            # Use is_authorized with explicit principal and attributes
            principal_id = decoded.get('sub', 'user')
            decision = vp.is_authorized(
                policyStoreId=POLICY_STORE_ID,
                principal={
                    'entityType': f'App::{PRINCIPAL_ENTITY_TYPE}',
                    'entityId': principal_id
                },
                action={'actionType': 'App::Action', 'actionId': action_id},
                resource={'entityType': 'App::Endpoint', 'entityId': resource_id},
                entities={
                    'entityList': [
                        {
                            'identifier': {
                                'entityType': f'App::{PRINCIPAL_ENTITY_TYPE}',
                                'entityId': principal_id
                            },
                            'attributes': {
                                'custom': {
                                    'record': {
                                        'role': {
                                            'string': user_role
                                        }
                                    }
                                },
                                'username': {
                                    'string': username
                                }
                            }
                        }
                    ]
                }
            )
        except (BotoCoreError, ClientError) as e:
            logger.error(f"AVP call failed: {e}")
            raise Exception('Unauthorized')

        if decision.get('decision', '').upper() != 'ALLOW':
            logger.warning(f"AVP denied access for {username} on {resource_id}")
            raise Exception('Unauthorized')

        logger.info(f"AVP decision: {decision.get('decision')}")
        
        # Generate the authorization response
        principal_id = decoded.get('sub', 'user')
        
        # Build resource ARN pattern - restrict to this method/path
        # methodArn format: arn:aws:execute-api:region:account-id:api-id/stage/VERB/resource-path
        resource_arn = method_arn or '*'
        
        auth_response = {
            'principalId': principal_id,
            'policyDocument': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Action': 'execute-api:Invoke',
                        'Effect': 'Allow',
                        'Resource': resource_arn
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
