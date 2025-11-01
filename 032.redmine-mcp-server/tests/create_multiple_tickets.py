#!/usr/bin/env python3
"""
Create multiple tickets based on examples/create-multiple-tickets-example.md
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def create_multiple_tickets():
    """Create multiple tickets as specified in the example"""
    
    # Get credentials from environment
    username = os.getenv('REDMINE_USERNAME')
    password = os.getenv('REDMINE_PASSWORD')
    
    if not username or not password:
        print("Error: REDMINE_USERNAME and REDMINE_PASSWORD must be set in .env file")
        return
    
    print(f"Using credentials: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    # Ticket specifications
    tickets = [
        {
            'subject': 'データベースパフォーマンス最適化',
            'description': 'データベースのクエリ最適化とインデックス見直しを実施。レスポンス時間の改善を目標とする。\nクエリ最適化も検討する'
        },
        {
            'subject': 'セキュリティ監査と脆弱性対応',
            'description': 'セキュリティ監査の実施とAPIエンドポイントの認証強化。OAuth2.0の導入を検討。'
        },
        {
            'subject': 'ユーザーインターフェース改善',
            'description': 'ユーザビリティテストの結果に基づくナビゲーション改善とモバイル対応強化。'
        },
        {
            'subject': 'クラウドインフラコスト最適化',
            'description': 'AWSリソースの見直しとコスト削減。EC2インスタンスサイズとS3ストレージクラスの最適化。'
        },
        {
            'subject': 'CI/CDパイプライン最適化',
            'description': 'GitHub Actionsワークフローの改善とテスト自動化の強化。デプロイ時間短縮を目標。'
        }
    ]
    
    try:
        # Login
        print("=== ログイン ===")
        login_result = scraper.login(username, password)
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return
        
        project_id = 'hoge-project'
        created_tickets = []
        
        print(f"\n=== {len(tickets)}個のチケット作成開始 ===")
        
        for i, ticket in enumerate(tickets, 1):
            print(f"\n--- チケット{i}: {ticket['subject']} ---")
            
            # Create ticket with common settings
            create_result = scraper.create_issue(
                project_id=project_id,
                subject=ticket['subject'],
                description=ticket['description']
            )
            
            if create_result['success']:
                issue_id = create_result['issue_id']
                created_tickets.append({
                    'id': issue_id,
                    'subject': ticket['subject'],
                    'url': create_result['issue_url']
                })
                print(f"OK 作成成功: チケット#{issue_id}")
                print(f"  URL: {create_result['issue_url']}")
            else:
                print(f"NG 作成失敗: {create_result['message']}")
        
        # Summary
        print(f"\n=== 作成結果サマリー ===")
        print(f"作成成功: {len(created_tickets)}/{len(tickets)} 件")
        
        if created_tickets:
            print("\n作成されたチケット:")
            for ticket in created_tickets:
                print(f"  #{ticket['id']}: {ticket['subject']}")
        
    finally:
        # Logout
        print("\n=== ログアウト ===")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    create_multiple_tickets()