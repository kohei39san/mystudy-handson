#!/usr/bin/env python3
"""
修正トラッカーで最小限のフィールドでチケット作成テスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
import config

def test_create_fix_minimal():
    """修正トラッカーで最小限のフィールドでチケット作成"""
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
        
        print("\n=== Creating minimal fix ticket ===")
        
        # 最小限のフィールドでテスト（以前成功したパターン）
        ticket_fields = {
            'issue_subject': 'Fix ticket - minimal test',
            'issue_status_id': '1',
            'issue_priority_id': '2'
        }
        
        print(f"Creating ticket with fields: {list(ticket_fields.keys())}")
        
        result = scraper.create_issue(project_id, tracker_id, **ticket_fields)
        
        if result['success']:
            print(f"\nStep 1: Minimal ticket created successfully!")
            print(f"   Ticket ID: #{result['issue_id']}")
            print(f"   URL: {result['issue_url']}")
            
            # 次に、親チケット、担当者、指摘者を追加してもう一つ作成
            print(f"\n=== Creating fix ticket with all fields ===")
            
            full_ticket_fields = {
                'issue_subject': 'Fix ticket with parent, assignee, reporter',
                'issue_status_id': '1',
                'issue_priority_id': '2',
                'issue_assigned_to_id': '1',  # admin
                'issue_parent_issue_id': result['issue_id'],  # Use the just created ticket as parent
                'issue_custom_field_values_3': '5'  # Reporter (k s)
            }
            
            print(f"Creating full ticket with fields: {list(full_ticket_fields.keys())}")
            
            full_result = scraper.create_issue(project_id, tracker_id, **full_ticket_fields)
            
            if full_result['success']:
                print(f"\nStep 2: Full ticket created successfully!")
                print(f"   Ticket ID: #{full_result['issue_id']}")
                print(f"   URL: {full_result['issue_url']}")
                
                # Get created ticket details
                print(f"\n=== Checking full ticket details ===")
                details_result = scraper.get_issue_details(full_result['issue_id'])
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
                print(f"\nStep 2: Full ticket creation failed: {full_result['message']}")
        else:
            print(f"\nStep 1: Minimal ticket creation failed: {result['message']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    test_create_fix_minimal()