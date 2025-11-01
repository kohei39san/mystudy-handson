#!/usr/bin/env python3
"""
修正トラッカーで親チケット、担当者、指摘者を指定してチケット作成テスト（シンプル版）
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
import config

def test_create_fix_ticket_simple():
    """修正トラッカーで親チケット、担当者、指摘者を指定してチケット作成"""
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Login...")
        username = os.getenv('REDMINE_USERNAME', 'kohei')
        password = os.getenv('REDMINE_PASSWORD', 'ariari_ssKK3')
        login_result = scraper.login(username, password)
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return
        print("Login successful")
        
        project_id = "hoge-project"
        tracker_id = "4"  # Fix tracker
        
        print("\n=== Creating fix ticket with parent, assignee, reporter ===")
        
        # まず利用可能なフィールドを確認
        print("Getting available fields...")
        fields_result = scraper.get_tracker_fields(project_id, tracker_id)
        if fields_result['success']:
            print(f"Available fields: {len(fields_result['fields'])}")
            for field in fields_result['fields']:
                if field['required'] or 'custom' in field.get('id', '').lower() or 'parent' in field.get('id', '').lower() or 'assigned' in field.get('id', '').lower():
                    print(f"  {field['id']}: {field['name']} ({'required' if field['required'] else 'optional'})")
        
        # 実際のフィールドIDを使用してチケット作成
        ticket_fields = {
            'issue_subject': 'Fix ticket with parent, assignee, reporter',
            'issue_description': 'This is a fix ticket with all fields specified.',
            'issue_status_id': '1',  # New
            'issue_priority_id': '2',  # Normal
            'issue_assigned_to_id': '1',  # admin
            'issue_parent_issue_id': '140',  # Parent ticket
            'issue_custom_field_values_3': '5'  # Reporter (k s)
        }
        
        print(f"Creating ticket with fields: {list(ticket_fields.keys())}")
        
        result = scraper.create_issue(project_id, tracker_id, **ticket_fields)
        
        if result['success']:
            print(f"\nTicket created successfully!")
            print(f"   Ticket ID: #{result['issue_id']}")
            print(f"   URL: {result['issue_url']}")
            
            # Get created ticket details
            print(f"\n=== Checking created ticket details ===")
            details_result = scraper.get_issue_details(result['issue_id'])
            if details_result['success']:
                issue = details_result['issue']
                print(f"Subject: {issue.get('subject', 'N/A')}")
                print(f"Tracker: {issue.get('tracker', 'N/A')}")
                print(f"Status: {issue.get('status', 'N/A')}")
                print(f"Priority: {issue.get('priority', 'N/A')}")
                print(f"Assignee: {issue.get('assigned_to', 'N/A')}")
                print(f"Parent: {issue.get('parent', 'N/A')}")
                print(f"Reporter: {issue.get('指摘者', 'N/A')}")
            else:
                print(f"Failed to get ticket details: {details_result['message']}")
        else:
            print(f"\nTicket creation failed: {result['message']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    test_create_fix_ticket_simple()