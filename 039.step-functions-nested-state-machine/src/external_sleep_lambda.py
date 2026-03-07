"""
External Lambda function (outside Step Functions state machine).
This function sleeps for 60 seconds to simulate a long-running external task.
"""
import json
import time


def lambda_handler(event, context):
    """
    Sleep for 60 seconds to simulate a long-running external process.

    Args:
        event: Input event (unused)
        context: Lambda context object

    Returns:
        dict: Completion result
    """
    print(f"External sleep Lambda received event: {json.dumps(event)}")

    time.sleep(60)

    response = {
        'statusCode': 200,
        'message': 'External sleep Lambda completed 60-second sleep'
    }

    print(f"External sleep Lambda returning: {json.dumps(response)}")
    return response
