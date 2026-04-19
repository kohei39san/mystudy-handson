#!/usr/bin/env python3
"""
Revoke API Test Script

このスクリプトは、revokeエンドポイントをテストするためのものです。
管理者権限を持つユーザーのトークンを使用して、指定されたユーザーのトークンを無効化します。

使用方法:
    python test-revoke-api.py --endpoint <API_ENDPOINT> --username <TARGET_USERNAME>

例:
    python test-revoke-api.py --endpoint https://abc123.execute-api.ap-northeast-1.amazonaws.com/dev --username testuser
"""

import argparse
import json
import requests
import sys
import time
from typing import Dict, Any, Optional


class RevokeAPITester:
    def __init__(self, api_endpoint: str):
        """
        Initialize the Revoke API Tester
        
        Args:
            api_endpoint: API Gateway endpoint URL
        """
        self.api_endpoint = api_endpoint.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'RevokeAPITester/1.0'
        })
    
    def authenticate_admin(self, username: str, password: str, user_pool_id: str, client_id: str) -> Optional[str]:
        """
        管理者ユーザーとして認証し、アクセストークンを取得
        
        Args:
            username: 管理者ユーザー名
            password: パスワード
            user_pool_id: Cognito User Pool ID
            client_id: Cognito Client ID
            
        Returns:
            アクセストークン（認証失敗時はNone）
        """
        import boto3
        from botocore.exceptions import ClientError
        
        try:
            cognito_client = boto3.client('cognito-idp')
            
            # AdminInitiateAuth を使用して認証
            response = cognito_client.admin_initiate_auth(
                UserPoolId=user_pool_id,
                ClientId=client_id,
                AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            access_token = response['AuthenticationResult']['AccessToken']
            print(f"✅ 管理者として認証成功: {username}")
            return access_token
            
        except ClientError as e:
            print(f"❌ 認証エラー: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            print(f"❌ 予期しないエラー: {str(e)}")
            return None
    
    def test_revoke_token(self, access_token: str, target_username: str) -> Dict[str, Any]:
        """
        revokeエンドポイントをテスト
        
        Args:
            access_token: 管理者のアクセストークン
            target_username: トークンを無効化する対象のユーザー名
            
        Returns:
            テスト結果
        """
        print(f"対象ユーザー: {target_username}")
        
        # リクエストヘッダーを設定
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # リクエストボディを作成
        request_body = {
            'username': target_username
        }
        
        try:
            # revokeエンドポイントにPOSTリクエストを送信
            response = self.session.post(
                f"{self.api_endpoint}/auth/revoke",
                headers=headers,
                json=request_body,
                timeout=30
            )
            
            # レスポンスを解析
            result = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'success': response.status_code == 200
            }
            
            try:
                result['body'] = response.json()
            except json.JSONDecodeError:
                result['body'] = response.text
            
            # 結果を表示
            if result['success']:
                print(f"✅ トークン無効化成功")
                print(f"ステータスコード: {result['status_code']}")
                if isinstance(result['body'], dict):
                    print(f"メッセージ: {result['body'].get('message', 'N/A')}")
                    print(f"対象ユーザー: {result['body'].get('username', 'N/A')}")
                    print(f"操作: {result['body'].get('operation', 'N/A')}")
            else:
                print(f"❌ トークン無効化失敗")
                print(f"ステータスコード: {result['status_code']}")
                if isinstance(result['body'], dict):
                    print(f"エラー: {result['body'].get('error', 'N/A')}")
                    print(f"メッセージ: {result['body'].get('message', 'N/A')}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ リクエストエラー: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status_code': None
            }
    
    def test_invalid_requests(self, access_token: str) -> None:
        """
        無効なリクエストのテスト
        
        Args:
            access_token: 管理者のアクセストークン
        """
        print(f"無効なリクエストのテストを開始します")
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # テストケース1: 空のリクエストボディ
        print("テストケース1: 空のリクエストボディ")
        try:
            response = self.session.post(
                f"{self.api_endpoint}/auth/revoke",
                headers=headers,
                json={},
                timeout=30
            )
            print(f"ステータスコード: {response.status_code}")
            if response.status_code == 400:
                print("✅ 期待通り400エラーが返されました")
            else:
                print("❌ 期待されるエラーが返されませんでした")
        except Exception as e:
            print(f"❌ リクエストエラー: {str(e)}")
        
        # テストケース2: 存在しないユーザー
        print("テストケース2: 存在しないユーザー")
        try:
            response = self.session.post(
                f"{self.api_endpoint}/auth/revoke",
                headers=headers,
                json={'username': 'nonexistent_user_12345'},
                timeout=30
            )
            print(f"ステータスコード: {response.status_code}")
            if response.status_code == 404:
                print("✅ 期待通り404エラーが返されました")
            else:
                print("❌ 期待されるエラーが返されませんでした")
        except Exception as e:
            print(f"❌ リクエストエラー: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Revoke API Test Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python test-revoke-api.py --endpoint https://abc123.execute-api.ap-northeast-1.amazonaws.com/dev --username testuser
  
注意:
  - 管理者権限を持つユーザーの認証情報が必要です
  - AWS認証情報が適切に設定されている必要があります
        """
    )
    
    parser.add_argument('--endpoint', required=True, help='API Gateway endpoint URL')
    parser.add_argument('--username', required=True, help='Target username to revoke tokens for')
    parser.add_argument('--admin-username', help='Admin username for authentication')
    parser.add_argument('--admin-password', help='Admin password for authentication')
    parser.add_argument('--user-pool-id', help='Cognito User Pool ID')
    parser.add_argument('--client-id', help='Cognito Client ID')
    
    args = parser.parse_args()
    
    # テスターを初期化
    tester = RevokeAPITester(args.endpoint)
    
    print("🚀 Revoke API テストを開始します")
    print(f"エンドポイント: {args.endpoint}")
    print(f"対象ユーザー: {args.username}")
    
    # 管理者として認証（認証情報が提供された場合）
    access_token = None
    if args.admin_username and args.admin_password and args.user_pool_id and args.client_id:
        access_token = tester.authenticate_admin(
            args.admin_username, args.admin_password, 
            args.user_pool_id, args.client_id
        )
    else:
        print("⚠️  認証情報が不完全です。手動でアクセストークンを設定してください。")
        access_token = input("管理者のアクセストークンを入力してください: ").strip()
    
    if not access_token:
        print("❌ アクセストークンが取得できませんでした")
        sys.exit(1)
    
    # revokeエンドポイントをテスト
    result = tester.test_revoke_token(access_token, args.username)
    
    # 無効なリクエストのテスト
    tester.test_invalid_requests(access_token)
    
    print(f"テスト完了")
    if result['success']:
        print("✅ 全体的な結果: 成功")
        sys.exit(0)
    else:
        print("❌ 全体的な結果: 失敗")
        sys.exit(1)


if __name__ == '__main__':
    main()
