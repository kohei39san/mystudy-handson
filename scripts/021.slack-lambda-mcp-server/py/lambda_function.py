import json
import os
import time
import boto3
import requests
import uuid
import logging
from datetime import datetime
import subprocess
import threading
import queue
import re

# ロギングの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 環境変数
OPENROUTER_API_KEY_PARAM = os.environ.get('OPENROUTER_API_KEY_PARAM', '/openrouter/api-key')
OPENROUTER_MODEL = os.environ.get('OPENROUTER_MODEL', 'deepseek/deepseek-chat-v3-0324:free')
OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'slack-mcp-bot-conversations')
AWS_DOCS_MCP_PORT = 8080
BEDROCK_KB_MCP_PORT = 8081
MAX_HISTORY_LENGTH = 10

# AWS クライアント
ssm_client = boto3.client('ssm')
dynamodb_client = boto3.client('dynamodb')
slack_client = boto3.client('lambda')
sns_client = boto3.client('sns')

# MCP サーバープロセス
aws_docs_mcp_process = None
bedrock_kb_mcp_process = None

# ストリーミングレスポンス用のキュー
response_queue = queue.Queue()

def get_parameter(param_name):
    """SSM パラメータストアから値を取得"""
    try:
        response = ssm_client.get_parameter(
            Name=param_name,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"Error retrieving parameter {param_name}: {str(e)}")
        raise

def start_mcp_servers():
    """MCP サーバーを起動"""
    global aws_docs_mcp_process, bedrock_kb_mcp_process
    
    # AWS Documentation MCP Server の起動
    try:
        aws_docs_mcp_process = subprocess.Popen(
            ["python", "-m", "aws_docs_mcp_server", "--port", str(AWS_DOCS_MCP_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.info(f"AWS Documentation MCP Server started on port {AWS_DOCS_MCP_PORT}")
    except Exception as e:
        logger.error(f"Failed to start AWS Documentation MCP Server: {str(e)}")
        raise
    
    # Bedrock Knowledge Base MCP Server の起動
    try:
        bedrock_kb_mcp_process = subprocess.Popen(
            ["python", "-m", "bedrock_kb_mcp_server", "--port", str(BEDROCK_KB_MCP_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.info(f"Bedrock Knowledge Base MCP Server started on port {BEDROCK_KB_MCP_PORT}")
    except Exception as e:
        logger.error(f"Failed to start Bedrock Knowledge Base MCP Server: {str(e)}")
        raise
    
    # サーバーの起動を待機
    time.sleep(2)

def stop_mcp_servers():
    """MCP サーバーを停止"""
    global aws_docs_mcp_process, bedrock_kb_mcp_process
    
    if aws_docs_mcp_process:
        aws_docs_mcp_process.terminate()
        aws_docs_mcp_process = None
        logger.info("AWS Documentation MCP Server stopped")
    
    if bedrock_kb_mcp_process:
        bedrock_kb_mcp_process.terminate()
        bedrock_kb_mcp_process = None
        logger.info("Bedrock Knowledge Base MCP Server stopped")

def get_conversation_history(user_id, channel_id):
    """DynamoDB から会話履歴を取得"""
    try:
        response = dynamodb_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={
                'userId': {'S': user_id},
                'channelId': {'S': channel_id}
            }
        )
        
        if 'Item' in response:
            history = json.loads(response['Item']['history']['S'])
            return history
        
        return []
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        return []

def save_conversation_history(user_id, channel_id, history):
    """DynamoDB に会話履歴を保存"""
    try:
        # 履歴の長さを制限
        if len(history) > MAX_HISTORY_LENGTH:
            history = history[-MAX_HISTORY_LENGTH:]
        
        dynamodb_client.put_item(
            TableName=DYNAMODB_TABLE,
            Item={
                'userId': {'S': user_id},
                'channelId': {'S': channel_id},
                'history': {'S': json.dumps(history)},
                'updatedAt': {'S': datetime.now().isoformat()}
            }
        )
    except Exception as e:
        logger.error(f"Error saving conversation history: {str(e)}")

def update_slack_message(channel_id, ts, text):
    """Slack メッセージを更新"""
    try:
        # Slack API を使用してメッセージを更新
        slack_url = "https://slack.com/api/chat.update"
        slack_token = get_parameter('/slack-bot/token')
        
        headers = {
            "Authorization": f"Bearer {slack_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "channel": channel_id,
            "ts": ts,
            "text": text
        }
        
        response = requests.post(slack_url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Error updating Slack message: {str(e)}")
        raise

def process_streaming_response(channel_id, ts, stream_response):
    """ストリーミングレスポンスを処理してSlackメッセージを更新"""
    full_response = ""
    last_update_time = time.time()
    update_interval = 1.0  # 1秒ごとに更新
    
    for line in stream_response.iter_lines():
        if line:
            try:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    data_str = line_text[6:]
                    if data_str.strip() == '[DONE]':
                        # ストリーミング完了
                        if full_response:
                            update_slack_message(channel_id, ts, full_response)
                        break
                    
                    data = json.loads(data_str)
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_response += content
                            
                            # 一定間隔でSlackメッセージを更新
                            current_time = time.time()
                            if current_time - last_update_time >= update_interval:
                                update_slack_message(channel_id, ts, full_response)
                                last_update_time = current_time
            except Exception as e:
                logger.error(f"Error processing streaming response: {str(e)}")
    
    # 最終更新
    if full_response:
        update_slack_message(channel_id, ts, full_response)
    
    return full_response

def call_openrouter_with_mcp(user_message, history, user_id):
    """OpenRouter API を呼び出し、MCP サーバーを使用"""
    try:
        # OpenRouter API キーを取得
        api_key = get_parameter(OPENROUTER_API_KEY_PARAM)
        
        # 会話履歴を構築
        messages = []
        for entry in history:
            role = "user" if entry["role"] == "user" else "assistant"
            messages.append({"role": role, "content": entry["content"]})
        
        # 現在のメッセージを追加
        messages.append({"role": "user", "content": user_message})
        
        # MCP サーバーの情報を含むシステムメッセージ
        system_message = """あなたは有用なAIアシスタントです。以下のツールを使用して質問に答えることができます：

1. AWS Documentation MCP Server (localhost:8080) - AWS公式ドキュメントを検索して情報を取得します
2. Amazon Bedrock Knowledge Bases Retrieval MCP Server (localhost:8081) - カスタムナレッジベースから情報を検索します

これらのツールを使用して、ユーザーの質問に正確に回答してください。必要に応じてツールを使用し、使用した場合はその結果を引用してください。"""
        
        # リクエストデータ
        data = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "system", "content": system_message}, *messages],
            "stream": True,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "aws_documentation_search",
                        "description": "Search AWS documentation for information",
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
                        "name": "bedrock_knowledge_base_search",
                        "description": "Search custom knowledge base for information",
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
            ]
        }
        
        # ヘッダー
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://aws-lambda-function.example",
            "X-Title": "AWS Lambda MCP Server"
        }
        
        # ストリーミングリクエスト
        response = requests.post(
            url=OPENROUTER_API_URL,
            headers=headers,
            json=data,
            stream=True
        )
        
        response.raise_for_status()
        return response
        
    except Exception as e:
        logger.error(f"Error calling OpenRouter API: {str(e)}")
        raise

def process_slack_message(message_data):
    """Slack メッセージを処理"""
    try:
        # メッセージデータを解析
        user_id = message_data['userId']
        channel_id = message_data['channelId']
        thread_ts = message_data.get('threadTs')
        message_ts = message_data.get('messageTs')
        response_ts = message_data.get('responseTs')
        text = message_data['text']
        
        # メンションを削除
        text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
        
        # 会話履歴を取得
        history = get_conversation_history(user_id, channel_id)
        
        # ユーザーメッセージを履歴に追加
        history.append({"role": "user", "content": text})
        
        # MCP サーバーを起動
        start_mcp_servers()
        
        try:
            # OpenRouter API を呼び出し
            stream_response = call_openrouter_with_mcp(text, history, user_id)
            
            # ストリーミングレスポンスを処理
            assistant_response = process_streaming_response(channel_id, response_ts, stream_response)
            
            # アシスタントの応答を履歴に追加
            history.append({"role": "assistant", "content": assistant_response})
            
            # 会話履歴を保存
            save_conversation_history(user_id, channel_id, history)
            
        finally:
            # MCP サーバーを停止
            stop_mcp_servers()
        
    except Exception as e:
        error_message = f"エラーが発生しました: {str(e)}"
        logger.error(error_message)
        
        # エラーメッセージをSlackに送信
        try:
            update_slack_message(channel_id, response_ts, f":x: {error_message}")
        except Exception as slack_error:
            logger.error(f"Failed to send error message to Slack: {str(slack_error)}")

def lambda_handler(event, context):
    """Lambda ハンドラー関数"""
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # SNSイベントを処理
        if 'Records' in event:
            for record in event['Records']:
                if record.get('EventSource') == 'aws:sns':
                    message = json.loads(record['Sns']['Message'])
                    message_type = record['Sns'].get('MessageAttributes', {}).get('messageType', {}).get('Value')
                    
                    if message_type == 'slack_message':
                        process_slack_message(message)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Processing complete')
        }
    
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }