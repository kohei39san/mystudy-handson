#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def main():
    redmine = RedmineSeleniumScraper()
    
    # Login
    print("Logging in...")
    login_result = redmine.login("admin", "admin")
    if not login_result['success']:
        print(f"Login failed: {login_result['message']}")
        return
    
    print("Login successful!")
    
    # Create ticket with 修正 tracker specifying reporter, assignee, and parent issue
    print("Creating ticket with 修正 tracker...")
    
    create_result = redmine.create_issue(
        project_id="hoge-project",
        issue_tracker_id="4",  # 修正 tracker
        issue_subject="修正トラッカーテストチケット - 指摘者・担当者・親チケット指定",
        issue_description="このチケットは修正トラッカーで作成され、指摘者、担当者、親チケットが指定されています。",
        issue_status_id="1",  # New status (required)
        issue_priority_id="2",  # Normal priority (required)
        issue_assigned_to_id="1",  # Admin as assignee (担当者)
        issue_parent_issue_id="134",  # Parent issue (親チケット) - using the ticket we just created
        issue_custom_field_values_3="1"  # Admin as reporter (指摘者)
    )
    
    if create_result['success']:
        print(f"[SUCCESS] Successfully created ticket: {create_result['message']}")
        print(f"  Issue ID: {create_result['issue_id']}")
        print(f"  Issue URL: {create_result['issue_url']}")
        
        # Get issue details to verify
        print("\\nVerifying created ticket...")
        details = redmine.get_issue_details(create_result['issue_id'])
        if details['success']:
            print("[SUCCESS] Ticket details:")
            for field, value in details['issue'].items():
                print(f"  {field}: {value}")
        else:
            print(f"[ERROR] Failed to get details: {details['message']}")
            
    else:
        print(f"[ERROR] Failed to create ticket: {create_result['message']}")
    
    # Logout
    redmine.logout()
    print("Logged out.")

if __name__ == "__main__":
    main()