"""
Child Lambda function for nested Step Functions state machine
This function processes input data and returns results
"""
import json


def lambda_handler(event, context):
    """
    Process input data from child state machine
    
    Args:
        event: Input event containing input_value and processing_type
        context: Lambda context object
        
    Returns:
        dict: Processed result
    """
    print(f"Child Lambda received event: {json.dumps(event)}")
    
    # Extract input parameters
    input_value = event.get('input_value', 0)
    processing_type = event.get('processing_type', 'multiply')
    
    # Process based on type
    if processing_type == 'multiply':
        result = input_value * 2
        operation = "multiplied by 2"
    elif processing_type == 'add':
        result = input_value + 10
        operation = "added 10"
    elif processing_type == 'square':
        result = input_value ** 2
        operation = "squared"
    else:
        result = input_value
        operation = "no operation"
    
    response = {
        'statusCode': 200,
        'processed_value': result,
        'original_value': input_value,
        'operation': operation,
        'processing_type': processing_type,
        'message': f'Child Lambda: {operation} to get {result}'
    }
    
    print(f"Child Lambda returning: {json.dumps(response)}")
    return response
