#!/usr/bin/env python3
"""
Test execution script for nested Step Functions state machine
This script starts an execution and monitors its progress
"""

import argparse
import json
import time
import boto3
from datetime import datetime


def start_execution(state_machine_arn, input_data, execution_name=None):
    """
    Start a Step Functions execution
    
    Args:
        state_machine_arn: ARN of the state machine to execute
        input_data: Input data as a dictionary
        execution_name: Optional execution name
        
    Returns:
        Execution ARN
    """
    client = boto3.client('stepfunctions')
    
    if not execution_name:
        execution_name = f"test-execution-{int(time.time())}"
    
    print(f"Starting execution: {execution_name}")
    print(f"Input data: {json.dumps(input_data, indent=2)}")
    
    response = client.start_execution(
        stateMachineArn=state_machine_arn,
        name=execution_name,
        input=json.dumps(input_data)
    )
    
    return response['executionArn']


def get_execution_status(execution_arn):
    """
    Get execution status and output
    
    Args:
        execution_arn: ARN of the execution
        
    Returns:
        Dictionary with status, output, and other details
    """
    client = boto3.client('stepfunctions')
    
    response = client.describe_execution(executionArn=execution_arn)
    
    result = {
        'status': response['status'],
        'start_date': response['startDate'],
    }
    
    if 'stopDate' in response:
        result['stop_date'] = response['stopDate']
        result['duration'] = (response['stopDate'] - response['startDate']).total_seconds()
    
    if 'output' in response:
        result['output'] = json.loads(response['output'])
    
    if 'error' in response:
        result['error'] = response.get('error')
        result['cause'] = response.get('cause')
    
    return result


def wait_for_execution(execution_arn, timeout=300, poll_interval=2):
    """
    Wait for execution to complete
    
    Args:
        execution_arn: ARN of the execution
        timeout: Maximum time to wait in seconds
        poll_interval: Time between status checks in seconds
        
    Returns:
        Final execution status
    """
    print(f"\nWaiting for execution to complete (timeout: {timeout}s)...")
    
    start_time = time.time()
    
    while True:
        status = get_execution_status(execution_arn)
        
        if status['status'] in ['SUCCEEDED', 'FAILED', 'TIMED_OUT', 'ABORTED']:
            return status
        
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print(f"Timeout after {elapsed:.1f} seconds")
            return status
        
        print(f"Status: {status['status']} (elapsed: {elapsed:.1f}s)")
        time.sleep(poll_interval)


def get_state_machine_arn_by_name(state_machine_name):
    """
    Get state machine ARN by name
    
    Args:
        state_machine_name: Name of the state machine
        
    Returns:
        State machine ARN
    """
    client = boto3.client('stepfunctions')
    
    response = client.list_state_machines()
    
    for sm in response['stateMachines']:
        if sm['name'] == state_machine_name:
            return sm['stateMachineArn']
    
    raise ValueError(f"State machine not found: {state_machine_name}")


def main():
    parser = argparse.ArgumentParser(
        description='Test nested Step Functions state machine execution'
    )
    parser.add_argument(
        '--state-machine-arn',
        help='ARN of the parent state machine'
    )
    parser.add_argument(
        '--state-machine-name',
        help='Name of the parent state machine (e.g., nested-sfn-study-dev-parent-sfn)'
    )
    parser.add_argument(
        '--initial-value',
        type=int,
        default=10,
        help='Initial value to process (default: 10)'
    )
    parser.add_argument(
        '--processing-type',
        choices=['multiply', 'add', 'square'],
        default='multiply',
        help='Type of processing (default: multiply)'
    )
    parser.add_argument(
        '--execution-name',
        help='Custom execution name'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Timeout in seconds (default: 300)'
    )
    
    args = parser.parse_args()
    
    # Get state machine ARN
    if args.state_machine_arn:
        state_machine_arn = args.state_machine_arn
    elif args.state_machine_name:
        state_machine_arn = get_state_machine_arn_by_name(args.state_machine_name)
    else:
        print("Error: Either --state-machine-arn or --state-machine-name must be provided")
        return 1
    
    print("===== Nested Step Functions State Machine Test =====")
    print(f"State Machine ARN: {state_machine_arn}")
    print("")
    
    # Prepare input data
    input_data = {
        'initial_value': args.initial_value,
        'processing_type': args.processing_type
    }
    
    # Start execution
    execution_arn = start_execution(
        state_machine_arn,
        input_data,
        args.execution_name
    )
    
    # Derive AWS region from the state machine ARN for the console URL
    region = ""
    try:
        region = state_machine_arn.split(":")[3]
    except (AttributeError, IndexError):
        region = ""
    
    if region:
        console_url = f"https://console.aws.amazon.com/states/home?region={region}#/executions/details/{execution_arn}"
    else:
        console_url = f"https://console.aws.amazon.com/states/home#/executions/details/{execution_arn}"
    
    print(f"\nExecution started: {execution_arn}")
    print(f"View in console: {console_url}")
    
    # Wait for completion
    final_status = wait_for_execution(execution_arn, args.timeout)
    
    # Display results
    print("\n===== Execution Results =====")
    print(f"Status: {final_status['status']}")
    print(f"Start Time: {final_status['start_date']}")
    
    if 'stop_date' in final_status:
        print(f"Stop Time: {final_status['stop_date']}")
        print(f"Duration: {final_status['duration']:.2f} seconds")
    
    if 'output' in final_status:
        print("\nOutput:")
        print(json.dumps(final_status['output'], indent=2))
    
    if 'error' in final_status:
        print(f"\nError: {final_status['error']}")
        print(f"Cause: {final_status['cause']}")
    
    # Return exit code based on status
    return 0 if final_status['status'] == 'SUCCEEDED' else 1


if __name__ == '__main__':
    exit(main())
