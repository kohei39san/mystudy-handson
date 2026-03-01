"""
Check completion Lambda function (inside Step Functions state machine).
Determines whether the external Lambda has completed by comparing the elapsed
time since invocation against the known sleep duration.
"""
import json
import time

SLEEP_DURATION_SECONDS = 60


def lambda_handler(event, context):
    """
    Check whether the external Lambda execution has completed.

    Args:
        event: Input event containing 'start_time' (Unix timestamp)
        context: Lambda context object

    Returns:
        dict: Completion status ('COMPLETED' or 'RUNNING') and elapsed time
    """
    print(f"Check completion Lambda received event: {json.dumps(event)}")

    start_time = event.get('start_time', 0)
    elapsed = int(time.time()) - start_time

    if elapsed >= SLEEP_DURATION_SECONDS:
        status = 'COMPLETED'
    else:
        status = 'RUNNING'

    result = {
        'statusCode': 200,
        'status': status,
        'start_time': start_time,
        'elapsed_seconds': elapsed,
        'message': f'Status: {status}, elapsed: {elapsed}s'
    }

    print(f"Check completion Lambda returning: {json.dumps(result)}")
    return result
