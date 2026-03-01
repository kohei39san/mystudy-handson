"""
Async invoke Lambda function (inside Step Functions state machine).
This function invokes the external sleep Lambda asynchronously and records
the invocation start time for completion tracking.
"""
import json
import os
import time

import boto3


def lambda_handler(event, context):
    """
    Invoke the external sleep Lambda asynchronously and return the start time.

    Args:
        event: Input event (unused)
        context: Lambda context object

    Returns:
        dict: Start time and status of the async invocation
    """
    print(f"Async invoke Lambda received event: {json.dumps(event)}")

    external_lambda_arn = os.environ['EXTERNAL_LAMBDA_ARN']

    lambda_client = boto3.client('lambda')

    start_time = int(time.time())

    response = lambda_client.invoke(
        FunctionName=external_lambda_arn,
        InvocationType='Event',
        Payload=json.dumps({'start_time': start_time})
    )

    print(f"Async invocation status: {response['StatusCode']}")

    result = {
        'statusCode': 200,
        'start_time': start_time,
        'status': 'RUNNING',
        'message': f'External Lambda invoked asynchronously at {start_time}'
    }

    print(f"Async invoke Lambda returning: {json.dumps(result)}")
    return result
