"""
Parent Lambda function for nested Step Functions state machine
This function handles pre-processing and post-processing
"""
import json


def lambda_handler(event, context):
    """
    Handle pre-processing and post-processing in parent state machine
    
    Args:
        event: Input event containing action type and data
        context: Lambda context object
        
    Returns:
        dict: Processing result
    """
    print(f"Parent Lambda received event: {json.dumps(event)}")
    
    action = event.get('action', 'unknown')
    
    if action == 'preprocess':
        # Pre-processing: Prepare data for child state machine
        input_data = event.get('data', {})
        initial_value = input_data.get('initial_value', 10)
        processing_type = input_data.get('processing_type', 'multiply')
        
        response = {
            'statusCode': 200,
            'value': initial_value,
            'processing_type': processing_type,
            'timestamp': context.aws_request_id,
            'message': f'Parent Lambda: Pre-processed with value {initial_value} and type {processing_type}'
        }
        
    elif action == 'postprocess':
        # Post-processing: Process output from child state machine
        child_output = event.get('child_output', {})
        original_data = event.get('original_data', {})
        
        processed_value = child_output.get('processed_value')
        original_value = child_output.get('original_value')
        operation = child_output.get('operation', 'unknown')

        if original_value is None:
            original_value = (
                original_data.get('preprocess_result', {})
                .get('preprocessed_data', {})
                .get('value', 0)
            )
        
        response = {
            'statusCode': 200,
            'final_value': processed_value,
            'original_value': original_value,
            'operation_performed': operation,
            'child_output': child_output,
            'message': f'Parent Lambda: Post-processed result - original: {original_value}, final: {processed_value}',
            'summary': f'Complete processing chain: {original_value} -> {operation} -> {processed_value}'
        }
        
    else:
        response = {
            'statusCode': 400,
            'error': f'Unknown action: {action}',
            'message': 'Parent Lambda: Invalid action specified'
        }
    
    print(f"Parent Lambda returning: {json.dumps(response)}")
    return response
