#!/usr/bin/env python3
"""
Create a ticket with assignee specified
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def create_assigned_ticket():
    """Create a ticket with assignee specified"""
    
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
        
        # First, get assignee options
        print("=== Getting assignee options ===")
        fields_result = scraper.get_tracker_fields(project_id, '4')
        
        assignee_options = []
        if fields_result['success']:
            for field in fields_result['fields']:
                if field['id'] == 'issue_assigned_to_id':
                    assignee_options = field.get('options', [])
                    break
        
        print(f"Assignee options: {len(assignee_options)}")
        for option in assignee_options[:10]:  # Show first 10 options
            print(f"  {option['value']}: {option['text']}")
        
        # Test 1: Create ticket with 'me' as assignee
        print("\n=== Test 1: Creating ticket with 'me' as assignee ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            tracker_id=4,  # 修正トラッカー
            subject='担当者指定テスト - me',
            description='担当者を「me」で指定したテストチケットです。',
            assigned_to_id='me'
        )
        
        if create_result['success']:
            print(f"OK 作成成功: チケット#{create_result['issue_id']}")
            print(f"URL: {create_result['issue_url']}")
        else:
            print(f"NG 作成失敗: {create_result['message']}")
        
        # Test 2: Create ticket with specific assignee ID (if available)
        if assignee_options:
            # Use first non-empty assignee option
            assignee_id = None
            for option in assignee_options:
                if option['value'] and option['value'] != '':
                    assignee_id = option['value']
                    assignee_name = option['text']
                    break
            
            if assignee_id:
                print(f"\n=== Test 2: Creating ticket with specific assignee ({assignee_name}) ===")
                create_result = scraper.create_issue(
                    project_id=project_id,
                    tracker_id=4,  # 修正トラッカー
                    subject=f'担当者指定テスト - {assignee_name}',
                    description=f'担当者を「{assignee_name}」で指定したテストチケットです。',
                    assigned_to_id=assignee_id
                )
                
                if create_result['success']:
                    print(f"OK 作成成功: チケット#{create_result['issue_id']}")
                    print(f"URL: {create_result['issue_url']}")
                    
                    # Check created ticket details
                    print("\n=== 作成されたチケットの詳細確認 ===")
                    details_result = scraper.get_issue_details(create_result['issue_id'])
                    
                    if details_result['success']:
                        issue = details_result['issue']
                        print(f"ID: {issue['id']}")
                        print(f"Subject: {issue.get('subject', 'Unknown')}")
                        print(f"Assigned to: {issue.get('担当者', 'Unknown')}")
                    else:
                        print(f"詳細取得失敗: {details_result['message']}")
                        
                else:
                    print(f"NG 作成失敗: {create_result['message']}")
            else:
                print("\n=== Test 2: No valid assignee options found ===")
        else:
            print("\n=== Test 2: No assignee options available ===")
        
    finally:
        scraper.logout()

if __name__ == "__main__":
    create_assigned_ticket()