#!/usr/bin/env python3
"""
Test script to create a ticket using 修正 tracker with parent ticket, assignee, and reporter
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
import time

def test_create_修正_ticket():
    """Test creating a ticket with 修正 tracker including parent ticket, assignee, and reporter"""
    
    # Initialize scraper
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in to Redmine...")
        login_result = scraper.login("admin", "admin")
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return False
        print("[OK] Login successful")
        
        # Get project info
        project_id = "hoge-project"
        
        # Get project members to find valid assignee
        print("Getting project members...")
        members_result = scraper.get_project_members(project_id)
        if not members_result['success']:
            print(f"Failed to get project members: {members_result['message']}")
            return False
        
        members = members_result['members']
        member_list = [f"{m['name']} (ID: {m['id']})" for m in members]
        print(f"Available members: {member_list}")
        
        # Use first available member as assignee
        assignee_id = members[0]['id'] if members else None
        assignee_name = members[0]['name'] if members else None
        
        if not assignee_id:
            print("No project members found for assignee")
            return False
        
        # Search for existing issues to use as parent
        print("Searching for existing issues to use as parent...")
        search_result = scraper.search_issues(project_id=project_id, per_page=5)
        if not search_result['success'] or not search_result['issues']:
            print("No existing issues found to use as parent")
            parent_id = None
        else:
            parent_id = search_result['issues'][0]['id']
            parent_subject = search_result['issues'][0]['subject']
            print(f"Using parent issue: #{parent_id} - {parent_subject}")
        
        # Create ticket with 修正 tracker
        print("Creating ticket with 修正 tracker...")
        
        # Prepare fields for 修正 tracker (ID: 4)
        fields = {
            'issue_description': 'テスト用の修正チケットです。\n\n修正内容:\n- バグの修正\n- テストケースの追加',
            'issue_assigned_to_id': assignee_id,
            'issue_status_id': '1',  # 新規 status
            'issue_priority_id': '2',  # 通常 priority
            'issue_custom_field_values_3': 'テスト指摘者'  # 指摘者 field
        }
        
        # Add parent ticket if available
        if parent_id:
            fields['issue_parent_issue_id'] = parent_id
        
        create_result = scraper.create_issue(
            project_id=project_id,
            issue_tracker_id='4',  # 修正 tracker
            issue_subject='修正チケットのテスト - バグ修正',
            fields=fields
        )
        
        if create_result['success']:
            issue_id = create_result['issue_id']
            print(f"[OK] Successfully created ticket #{issue_id}")
            print(f"  Subject: 修正チケットのテスト - バグ修正")
            print(f"  Tracker: 修正")
            print(f"  Assignee: {assignee_name} (ID: {assignee_id})")
            print(f"  Reporter (指摘者): テスト指摘者")
            if parent_id:
                print(f"  Parent Issue: #{parent_id}")
            print(f"  URL: {create_result.get('issue_url', 'N/A')}")
            
            # Verify the created ticket
            print("\nVerifying created ticket...")
            details_result = scraper.get_issue_details(issue_id)
            if details_result['success']:
                issue = details_result['issue']
                print(f"[OK] Verification successful:")
                print(f"  ID: #{issue['id']}")
                print(f"  Subject: {issue['subject']}")
                print(f"  Tracker: {issue['tracker']}")
                print(f"  Status: {issue['status']}")
                print(f"  Assignee: {issue.get('assigned_to', 'Not assigned')}")
                if issue.get('parent'):
                    print(f"  Parent: {issue['parent']}")
                if issue.get('custom_fields'):
                    for cf in issue['custom_fields']:
                        if '指摘者' in cf.get('name', ''):
                            print(f"  指摘者: {cf.get('value', 'Not set')}")
            else:
                print(f"Failed to verify ticket: {details_result['message']}")
            
            return True
        else:
            print(f"[ERROR] Failed to create ticket: {create_result['message']}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")
        return False
    finally:
        # Cleanup
        try:
            scraper.logout()
            scraper.close()
        except:
            pass

if __name__ == "__main__":
    print("=== Test: Create 修正 Ticket with Parent, Assignee, and Reporter ===")
    success = test_create_修正_ticket()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)