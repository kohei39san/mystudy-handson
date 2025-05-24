#!/usr/bin/env python3
"""
ローカル環境でLambda関数をテストするためのスクリプト
"""

import json
import os
import boto3
import dotenv
from lambda_function import lambda_handler, process_slack_message

# .env ファイルから環境変数を読み込む
dotenv.load_dotenv()

def get_ssm_parameter(param_name):
    """SSM パラメータストアから値を取得"""
    try:
        ssm_client = boto3.client('ssm')
        response = ssm_client.get_parameter(
            Name=param_name,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        print(f"SSM パラメータの取得に失敗しました: {str(e)}")
        return None

def load_config_from_ssm():
    """SSM パラメータストアから設定を読み込む"""
    try:
        # SSM パラメータストアから設定を取得
        config = {}
        
        # テスト用のメッセージデータを取得
        config['userId'] = get_ssm_parameter('/slack-mcp-server/test/userId') or 'U12345678'
        config['channelId'] = get_ssm_parameter('/slack-mcp-server/test/channelId') or 'C12345678'
        config['responseTs'] = get_ssm_parameter('/slack-mcp-server/test/responseTs') or '1234567890.123456'
        config['text'] = get_ssm_parameter('/slack-mcp-server/test/text') or 'AWS Lambda について教えてください'
        
        # 環境変数の設定値を取得
        config['OPENROUTER_API_KEY_PARAM'] = get_ssm_parameter('/slack-mcp-server/openrouter/api-key-param') or '/openrouter/api-key'
        config['OPENROUTER_MODEL'] = get_ssm_parameter('/slack-mcp-server/openrouter/model') or 'anthropic/claude-3-opus:beta'
        config['DYNAMODB_TABLE'] = get_ssm_parameter('/slack-mcp-server/dynamodb/table') or 'slack-mcp-bot-conversations'
        
        return config
    except Exception as e:
        print(f"SSM パラメータストアからの設定読み込みに失敗しました: {str(e)}")
        return {}

def setup_local_environment():
    """ローカルテスト用の環境変数を設定"""
    # SSM パラメータストアから環境変数を読み込む
    config = load_config_from_ssm()
    
    # 環境変数を設定
    for key, value in config.items():
        if key not in ['userId', 'channelId', 'responseTs', 'text']:
            os.environ[key] = value
    
    print("環境変数の設定が完了しました")

def test_lambda_handler():
    """Lambda ハンドラー関数をテスト"""
    # SSM パラメータストアからメッセージデータを読み込む
    config = load_config_from_ssm()
    message_data = {
        'userId': config.get('userId', 'U12345678'),
        'channelId': config.get('channelId', 'C12345678'),
        'responseTs': config.get('responseTs', '1234567890.123456'),
        'text': config.get('text', 'AWS Lambda について教えてください')
    }
    
    # SNSイベントをシミュレート
    event = {
        'Records': [
            {
                'EventSource': 'aws:sns',
                'Sns': {
                    'Message': json.dumps(message_data),
                    'MessageAttributes': {
                        'messageType': {
                            'Value': 'slack_message'
                        }
                    }
                }
            }
        ]
    }
    
    # Lambda ハンドラーを呼び出し
    try:
        response = lambda_handler(event, {})
        print(f"Lambda ハンドラーのレスポンス: {response}")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

def test_direct_message_processing():
    """Slack メッセージ処理関数を直接テスト"""
    # SSM パラメータストアからメッセージデータを読み込む
    config = load_config_from_ssm()
    message_data = {
        'userId': config.get('userId', 'U12345678'),
        'channelId': config.get('channelId', 'C12345678'),
        'responseTs': config.get('responseTs', '1234567890.123456'),
        'text': config.get('text', 'AWS Lambda について教えてください')
    }
    
    # メッセージ処理関数を呼び出し
    try:
        process_slack_message(message_data)
        print("メッセージ処理が完了しました")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

def main():
    """メイン関数"""
    print("MCP サーバーのローカルテストを開始します")
    
    # 環境変数の設定
    setup_local_environment()
    
    # テストの種類を選択
    print("\nテストの種類を選択してください:")
    print("1. Lambda ハンドラー関数をテスト")
    print("2. Slack メッセージ処理関数を直接テスト")
    
    choice = input("選択 (1 または 2): ")
    
    if choice == '1':
        test_lambda_handler()
    elif choice == '2':
        test_direct_message_processing()
    else:
        print("無効な選択です。1 または 2 を入力してください。")

if __name__ == "__main__":
    main()