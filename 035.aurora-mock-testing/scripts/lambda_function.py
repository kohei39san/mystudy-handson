import json
from custom_utils import format_response, validate_config


def lambda_handler(event, context):
    return format_response("success", {"message": "Hello from Lambda with custom utils"})