"""Custom utility functions for Lambda layer"""

def format_response(status: str, data: dict) -> dict:
    """Format API response"""
    return {"status": status, "data": data}

def validate_config(config: dict) -> bool:
    """Validate configuration"""
    required = ['host', 'port', 'dbname']
    return all(k in config for k in required)
