import json
import os
import time
import boto3
import requests
import threading
import subprocess
import logging
from typing import List, Dict, Any, Optional
import uuid
import signal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ssm = boto3.client('ssm')
dynamodb = boto3.resource('dynamodb')

# Global variables
aws_docs_mcp_server_process = None
bedrock_kb_mcp_server_process = None
aws_docs_mcp_server_port = int(os.environ.get('AWS_DOCS_MCP_SERVER_PORT', 8080))
bedrock_kb_mcp_server_port = int(os.environ.get('BEDROCK_KB_MCP_SERVER_PORT', 8081))

# Table for conversation history
conversation_table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'slack-mcp-conversations'))

def get_parameter(name: str) -> str:
    """
    Get a parameter from SSM Parameter Store
    """
    response = ssm.get_parameter(
        Name=name,
        WithDecryption=True
    )
    return response['Parameter']['Value']

def start_mcp_servers():
    """
    Start the MCP servers as background processes
    """
    global aws_docs_mcp_server_process, bedrock_kb_mcp_server_process
    
    # Start AWS Documentation MCP Server
    logger.info(f"Starting AWS Documentation MCP Server on port {aws_docs_mcp_server_port}")
    aws_docs_mcp_server_process = subprocess.Popen(
        [
            "python", "-m", "aws_mcp_server.aws_docs_mcp_server",
            "--port", str(aws_docs_mcp_server_port)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Start Bedrock Knowledge Base MCP Server
    logger.info(f"Starting Bedrock Knowledge Base MCP Server on port {bedrock_kb_mcp_server_port}")
    bedrock_kb_mcp_server_process = subprocess.Popen(
        [
            "python", "-m", "aws_mcp_server.bedrock_kb_mcp_server",
            "--port", str(bedrock_kb_mcp_server_port),
            "--kb-id", os.environ.get('BEDROCK_KB_ID', ''),
            "--region", os.environ.get('AWS_REGION', 'us-east-1')
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the servers time to start
    time.sleep(2)
    
    # Check if servers started successfully
    if aws_docs_mcp_server_process.poll() is not None:
        stderr = aws_docs_mcp_server_process.stderr.read().decode('utf-8')
        raise Exception(f"AWS Documentation MCP Server failed to start: {stderr}")
    
    if bedrock_kb_mcp_server_process.poll() is not None:
        stderr = bedrock_kb_mcp_server_process.stderr.read().decode('utf-8')
        raise Exception(f"Bedrock Knowledge Base MCP Server failed to start: {stderr}")
    
    logger.info("Both MCP servers started successfully")

def stop_mcp_servers():
    """
    Stop the MCP servers
    """
    global aws_docs_mcp_server_process, bedrock_kb_mcp_server_process
    
    if aws_docs_mcp_server_process:
        logger.info("Stopping AWS Documentation MCP Server")
        aws_docs_mcp_server_process.terminate()
        aws_docs_mcp_server_process.wait(timeout=5)
    
    if bedrock_kb_mcp_server_process:
        logger.info("Stopping Bedrock Knowledge Base MCP Server")
        bedrock_kb_mcp_server_process.terminate()
        bedrock_kb_mcp_server_process.wait(timeout=5)

def format_conversation_history(conversation_history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Format the conversation history for OpenRouter
    """
    formatted_history = []
    
    for item in conversation_history:
        role = "assistant" if item.get('type') == 'bot_response' else "user"
        formatted_history.append({
            "role": role,
            "content": item.get('text', '')
        })
    
    return formatted_history

def query_openrouter(message: str, conversation_history: List[Dict[str, Any]]) -> str:
    """
    Query OpenRouter with the message and conversation history
    """
    try:
        # Get OpenRouter API key from SSM
        openrouter_api_key = get_parameter('/slack-mcp-bot/OPENROUTER_API_KEY')
        
        # Format conversation history
        formatted_history = format_conversation_history(conversation_history)
        
        # Prepare the system message with MCP server information
        system_message = """You are an AI assistant with access to the following tools:
1. AWS Documentation MCP Server - For querying AWS documentation
2. Amazon Bedrock Knowledge Bases Retrieval MCP Server - For retrieving information from custom knowledge bases

When a user asks a question that might benefit from these tools, use them appropriately.
To use the AWS Documentation MCP Server, you can search for AWS service documentation.
To use the Bedrock Knowledge Base MCP Server, you can retrieve information from the knowledge base.

Respond in a helpful, accurate, and concise manner. If you don't know the answer or if the tools don't provide relevant information, be honest about it."""
        
        # Prepare the message for OpenRouter
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add conversation history
        messages.extend(formatted_history)
        
        # Add the current message
        messages.append({"role": "user", "content": message})
        
        # Prepare the payload for OpenRouter
        payload = {
            "model": "anthropic/claude-3-opus:beta",
            "messages": messages,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "query_aws_docs",
                        "description": "Query AWS documentation for information about AWS services, features, and concepts",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query for AWS documentation"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "query_knowledge_base",
                        "description": "Query the Bedrock knowledge base for information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query for the knowledge base"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                }
            ],
            "tool_choice": "auto"
        }
        
        # Send the request to OpenRouter
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        response_data = response.json()
        
        # Process the response
        if 'choices' in response_data and len(response_data['choices']) > 0:
            message_content = response_data['choices'][0]['message']
            
            # Check if there are tool calls
            if 'tool_calls' in message_content:
                tool_calls = message_content['tool_calls']
                
                # Process each tool call
                for tool_call in tool_calls:
                    function_call = tool_call.get('function', {})
                    function_name = function_call.get('name')
                    function_args = json.loads(function_call.get('arguments', '{}'))
                    
                    if function_name == 'query_aws_docs':
                        # Call AWS Documentation MCP Server
                        query = function_args.get('query', '')
                        aws_docs_result = call_aws_docs_mcp_server(query)
                        
                        # Add the function result to the messages
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        })
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call['id'],
                            "name": function_name,
                            "content": json.dumps(aws_docs_result)
                        })
                    
                    elif function_name == 'query_knowledge_base':
                        # Call Bedrock Knowledge Base MCP Server
                        query = function_args.get('query', '')
                        kb_result = call_bedrock_kb_mcp_server(query)
                        
                        # Add the function result to the messages
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        })
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call['id'],
                            "name": function_name,
                            "content": json.dumps(kb_result)
                        })
                
                # Make a second call to OpenRouter with the tool results
                second_payload = {
                    "model": "anthropic/claude-3-opus:beta",
                    "messages": messages
                }
                
                second_response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=second_payload
                )
                
                second_response_data = second_response.json()
                
                if 'choices' in second_response_data and len(second_response_data['choices']) > 0:
                    return second_response_data['choices'][0]['message']['content']
                else:
                    raise Exception(f"Error in second OpenRouter call: {second_response_data}")
            
            # If no tool calls, return the content directly
            return message_content['content']
        else:
            raise Exception(f"Error in OpenRouter response: {response_data}")
    
    except Exception as e:
        logger.error(f"Error querying OpenRouter: {str(e)}")
        raise

def call_aws_docs_mcp_server(query: str) -> Dict[str, Any]:
    """
    Call the AWS Documentation MCP Server
    """
    try:
        response = requests.post(
            f"http://localhost:{aws_docs_mcp_server_port}/query",
            json={"query": query}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error calling AWS Documentation MCP Server: {response.text}")
            return {"error": f"Error: {response.status_code}", "results": []}
    
    except Exception as e:
        logger.error(f"Exception calling AWS Documentation MCP Server: {str(e)}")
        return {"error": str(e), "results": []}

def call_bedrock_kb_mcp_server(query: str) -> Dict[str, Any]:
    """
    Call the Bedrock Knowledge Base MCP Server
    """
    try:
        response = requests.post(
            f"http://localhost:{bedrock_kb_mcp_server_port}/query",
            json={"query": query}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error calling Bedrock KB MCP Server: {response.text}")
            return {"error": f"Error: {response.status_code}", "results": []}
    
    except Exception as e:
        logger.error(f"Exception calling Bedrock KB MCP Server: {str(e)}")
        return {"error": str(e), "results": []}

def handler(event, context):
    """
    Lambda handler function
    """
    try:
        # Start MCP servers
        start_mcp_servers()
        
        # Extract information from the event
        message = event.get('message', '')
        user_id = event.get('userId', '')
        channel_id = event.get('channelId', '')
        thread_ts = event.get('threadTs', '')
        conversation_history = event.get('conversationHistory', [])
        
        # Query OpenRouter
        response = query_openrouter(message, conversation_history)
        
        # Return the response
        return {
            'statusCode': 200,
            'response': response
        }
    
    except Exception as e:
        logger.error(f"Error in Lambda handler: {str(e)}")
        return {
            'statusCode': 500,
            'error': str(e)
        }
    
    finally:
        # Stop MCP servers
        stop_mcp_servers()

# For local testing
if __name__ == "__main__":
    test_event = {
        'message': 'How do I set up an S3 bucket?',
        'userId': 'U12345678',
        'channelId': 'C12345678',
        'threadTs': '1234567890.123456',
        'conversationHistory': []
    }
    
    print(json.dumps(handler(test_event, None), indent=2))