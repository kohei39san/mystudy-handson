#!/usr/bin/env python3
"""
Create a ticket with parent issue and reporter specified
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def create_parent_ticket():
    """Create a ticket with parent issue and reporter"""
    
    # Get credentials from environment
    username = os.getenv('REDMINE_USERNAME')
    password = os.getenv('REDMINE_PASSWORD')
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        login_result = scraper.login(username, password)
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return
        
        project_id = 'hoge-project'
        
        # Create ticket with parent issue and reporter
        print("=== 親チケット・指摘者指定チケット作成 ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            tracker_id=4,  # 修正トラッカー
            subject='システム改善プロジェクト - 子チケット',
            description='親チケットに関連する修正作業です。指摘者からの要求に基づいて実施します。',
            parent_id='121',  # 親チケットID（データベースパフォーマンス最適化）
            assigned_to_id='me'  # 担当者は自分
        )
        
        if create_result['success']:
            print(f"OK 作成成功: チケット#{create_result['issue_id']}")
            print(f"URL: {create_result['issue_url']}")
            
            # 作成されたチケットの詳細を確認
            print("\n=== 作成されたチケットの詳細確認 ===")
            details_result = scraper.get_issue_details(create_result['issue_id'])
            
            if details_result['success']:
                issue = details_result['issue']
                print(f"ID: {issue['id']}")
                print(f"Subject: {issue.get('subject', 'Unknown')}")
                print(f"Tracker: {issue.get('tracker', 'Unknown')}")
                print(f"Status: {issue.get('status', 'Unknown')}")
                print(f"Priority: {issue.get('priority', 'Unknown')}")
                print(f"Assigned to: {issue.get('担当者', 'Unknown')}")
                print(f"Description: {issue.get('description', 'Unknown')}")
                
                # 親チケット情報があるかチェック
                parent_fields = [k for k in issue.keys() if 'parent' in k.lower() or '親' in k]
                if parent_fields:
                    print("Parent fields found:")
                    for field in parent_fields:
                        print(f"  {field}: {issue[field]}")
                else:
                    print("No parent fields found in response")
            else:
                print(f"詳細取得失敗: {details_result['message']}")
                
        else:
            print(f"NG 作成失敗: {create_result['message']}")
        
    finally:
        scraper.logout()

if __name__ == "__main__":
    create_parent_ticket()