#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
import config

def test_fix_tracker_with_fields():
    scraper = RedmineSeleniumScraper()
    
    # Login
    import os
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    login_result = scraper.login(username, password)
    if not login_result['success']:
        print(f"Login failed: {login_result['message']}")
        return
    
    print("Login successful")
    
    # Get project members to find a valid user ID
    members_result = scraper.get_project_members('hoge-project')
    if not members_result['success']:
        print(f"Failed to get project members: {members_result['message']}")
        scraper.logout()
        return
    
    members = members_result['members']
    print(f"Found {len(members)} project members:")
    for member in members:
        print(f"  - {member.get('name')} (ID: {member.get('id')})")
    
    # Use first member as assignee
    assignee_id = members[0]['id'] if members else '1'
    
    # Create issue with 修正 tracker (ID: 4) and various fields
    issue_data = {
        'tracker_id': '4',  # 修正トラッカー
        'subject': 'テスト修正チケット - 親チケット・担当者・指摘者指定',
        'issue_description': '修正トラッカーでのフィールド指定テスト',
        'issue_parent_issue_id': '120',  # 親チケット
        'issue_assigned_to_id': assignee_id,  # 担当者（ユーザID）
        'issue_custom_field_values_3': assignee_id,  # 指摘者（カスタムフィールド）
        'issue_priority_id': '2',  # 通常
        'issue_status_id': '1'  # 新規
    }
    
    print(f"\nCreating issue with data:")
    for key, value in issue_data.items():
        print(f"  {key}: {value}")
    
    result = scraper.create_issue('hoge-project', **issue_data)
    
    if result['success']:
        print(f"\nIssue created successfully!")
        print(f"  Issue ID: {result['issue_id']}")
        print(f"  URL: {result['issue_url']}")
        
        # Get issue details to verify fields were set
        details_result = scraper.get_issue_details(result['issue_id'])
        if details_result['success']:
            issue = details_result['issue']
            print(f"\nIssue details:")
            print(f"  Subject: {issue.get('subject')}")
            print(f"  Tracker: {issue.get('tracker')}")
            print(f"  Status: {issue.get('status')}")
            print(f"  Priority: {issue.get('priority')}")
            print(f"  Assigned to: {issue.get('担当者', issue.get('assigned_to'))}")
            print(f"  Parent: {issue.get('親チケット', issue.get('parent'))}")
            print(f"  Reporter: {issue.get('指摘者', issue.get('reporter'))}")
    else:
        print(f"\nIssue creation failed: {result['message']}")
    
    scraper.logout()

if __name__ == "__main__":
    test_fix_tracker_with_fields()