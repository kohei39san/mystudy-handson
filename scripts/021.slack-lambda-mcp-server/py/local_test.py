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

def setup_local_environment():
    """ローカルテスト用の環境変数を設定"""
    # 必要な環境変数が設定されていない場合はデフォルト値を設定
    if 'OPENROUTER_API_KEY_PARAM' not in os.environ:
        os.environ['OPENROUTER_API_KEY_PARAM'] = '/openrouter/api-key'
    
    if 'OPENROUTER_MODEL' not in os.environ:
        os.environ['OPENROUTER_MODEL'] = 'anthropic/claude-3-opus:beta'
    
    if 'DYNAMODB_TABLE' not in os.environ:
        os.environ['DYNAMODB_TABLE'] = 'slack-mcp-bot-conversations'
    
    print("環境変数の設定が完了しました")

def test_lambda_handler():
    """Lambda ハンドラー関数をテスト"""
    # SNSイベントをシミュレート
    event = {
        'Records': [
            {
                'EventSource': 'aws:sns',
                'Sns': {
                    'Message': json.dumps({
                        'userId': 'U12345678',
                        'channelId': 'C12345678',
                        'responseTs': '1234567890.123456',
                        'text': 'AWS Lambda について教えてください'
                    }),
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
    # メッセージデータ
    message_data = {
        'userId': 'U12345678',
        'channelId': 'C12345678',
        'responseTs': '1234567890.123456',
        'text': 'AWS Lambda について教えてください'
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