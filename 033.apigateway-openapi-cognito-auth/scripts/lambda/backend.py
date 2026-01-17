"""
Backend Lambda Function for API Gateway OpenAPI Cognito Auth

This function handles the main API endpoints:
- /health: Health check endpoint
- /public: Public endpoint (authentication required)
- /user: User endpoint (user role required)
- /admin: Admin endpoint (admin role required)
"""

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Main Lambda handler"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Get request context
        resource = event.get('resource', '')
        method = event.get('httpMethod', '')
        path = event.get('path', '')
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Get authorizer context
        authorizer = event.get('requestContext', {}).get('authorizer', {})
        user_role = authorizer.get('custom:role', 'unknown')
        username = authorizer.get('claims', {}).get('cognito:username', 'unknown') if isinstance(authorizer.get('claims'), dict) else 'unknown'
        
        logger.info(f"Path: {path}, Method: {method}, User: {username}, Role: {user_role}")
        
        # Route based on path
        if path == '/health':
            return handle_health(event, context)
        elif path == '/public':
            return handle_public(event, context, username, user_role)
        elif path == '/user':
            return handle_user(event, context, username, user_role)
        elif path == '/admin':
            return handle_admin(event, context, username, user_role)
        else:
            return error_response(404, f"Path not found: {path}")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return error_response(500, f"Internal server error: {str(e)}")


def handle_health(event, context):
    """Handle /health endpoint"""
    return success_response({
        "status": "healthy",
        "message": "Backend Lambda is running",
        "service": "openapi-cognito-auth"
    })


def handle_public(event, context, username, user_role):
    """Handle /public endpoint (authentication required)"""
    query_params = event.get('queryStringParameters', {}) or {}
    format_param = query_params.get('format', 'json')
    
    return success_response({
        "message": f"Welcome {username}! You have access to the public endpoint.",
        "user": username,
        "role": user_role,
        "format": format_param,
        "data": {
            "public_info": "This is publicly accessible to authenticated users"
        }
    })


def handle_user(event, context, username, user_role):
    """Handle /user endpoint (user role required)"""
    query_params = event.get('queryStringParameters', {}) or {}
    filter_param = query_params.get('filter', 'all')
    limit_param = int(query_params.get('limit', 10))
    
    if user_role not in ['user', 'admin']:
        return error_response(403, f"User role '{user_role}' is not authorized for this endpoint")
    
    return success_response({
        "message": f"User data for {username}",
        "user": username,
        "role": user_role,
        "filter": filter_param,
        "limit": limit_param,
        "data": [
            {"id": 1, "name": "Item 1", "description": "First item"},
            {"id": 2, "name": "Item 2", "description": "Second item"},
            {"id": 3, "name": "Item 3", "description": "Third item"}
        ][:limit_param]
    })


def handle_admin(event, context, username, user_role):
    """Handle /admin endpoint (admin role required)"""
    body = json.loads(event.get('body', '{}')) if event.get('body') else {}
    query_params = event.get('queryStringParameters', {}) or {}
    
    action = query_params.get('action', 'info')
    target = query_params.get('target', 'system')
    
    if user_role != 'admin':
        return error_response(403, f"User role '{user_role}' is not authorized for admin endpoint")
    
    return success_response({
        "message": f"Admin action '{action}' executed by {username}",
        "user": username,
        "role": user_role,
        "action": action,
        "target": target,
        "result": {
            "status": "success",
            "action_performed": action,
            "target_resource": target
        }
    })


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
