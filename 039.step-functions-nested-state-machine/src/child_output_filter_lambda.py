"""
Filter child state machine output for the parent state machine.
This function echoes back the filtered input.
"""
import json


def lambda_handler(event, context):
    """
    Echo the filtered child output.

    Args:
        event: Filtered input payload
        context: Lambda context object

    Returns:
        dict: Echoed payload
    """
    print(f"Child output filter received event: {json.dumps(event)}")
    response = event or {}
    print(f"Child output filter returning: {json.dumps(response)}")
    return response
