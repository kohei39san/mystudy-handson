#!/usr/bin/env python3
"""
Create a ticket with parent issue and reporter specified using correct field names
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def create_parent_reporter_ticket():
    """Create a ticket with parent issue and reporter using correct field names"""
    
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
        
        # First, get reporter field options
        print("=== Getting reporter field options ===")
        fields_result = scraper.get_tracker_fields(project_id, '4')
        
        reporter_options = []
        if fields_result['success']:
            for field in fields_result['fields']:
                if field['id'] == 'issue_custom_field_values_3':
                    reporter_options = field.get('options', [])
                    break
        
        print(f"Reporter options: {len(reporter_options)}")
        for option in reporter_options[:5]:  # Show first 5 options
            print(f"  {option['value']}: {option['text']}")
        
        # Create ticket with parent issue and reporter
        print("\n=== Creating ticket with parent and reporter ===")
        
        # Use first available reporter option if available
        reporter_id = reporter_options[0]['value'] if reporter_options else None
        
        create_result = scraper.create_issue(
            project_id=project_id,
            tracker_id=4,  # 修正トラッカー
            subject='システム改善プロジェクト - 親チケット・指摘者指定',
            description='親チケットに関連する修正作業です。指摘者からの要求に基づいて実施します。',
            parent_id='121',  # 親チケットID
            custom_field_values_3=reporter_id,  # 指摘者ID
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
                print(f"Reporter: {issue.get('指摘者', 'Unknown')}")
                print(f"Description: {issue.get('description', 'Unknown')}")
                
                # Show all fields for debugging
                print(f"\nAll fields ({len(issue)} total):")
                for key, value in issue.items():
                    print(f"  {key}: {value}")
                    
            else:
                print(f"詳細取得失敗: {details_result['message']}")
                
        else:
            print(f"NG 作成失敗: {create_result['message']}")
        
    finally:
        scraper.logout()

if __name__ == "__main__":
    create_parent_reporter_ticket()