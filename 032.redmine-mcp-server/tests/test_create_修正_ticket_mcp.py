#!/usr/bin/env python3
"""
Test script to create a ticket using 修正 tracker with parent ticket, assignee, and reporter via MCP server
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import asyncio
from redmine_mcp_server import RedmineMCPServer

async def test_create_修正_ticket_mcp():
    """Test creating a ticket with 修正 tracker via MCP server"""
    
    server = RedmineMCPServer()
    
    try:
        # Login
        print("Logging in to Redmine...")
        login_result = await server.handle_redmine_login(
            username="admin",
            password="admin"
        )
        if not login_result.get('success'):
            print(f"Login failed: {login_result.get('message')}")
            return False
        print("[OK] Login successful")
        
        # Get project members
        print("Getting project members...")
        members_result = await server.handle_get_project_members(project_id="hoge-project")
        if not members_result.get('success'):
            print(f"Failed to get project members: {members_result.get('message')}")
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
        search_result = await server.handle_search_issues(project_id="hoge-project", per_page=5)
        if not search_result.get('success') or not search_result.get('issues'):
            print("No existing issues found to use as parent")
            parent_id = None
        else:
            parent_id = search_result['issues'][0]['id']
            parent_subject = search_result['issues'][0]['subject']
            print(f"Using parent issue: #{parent_id} - {parent_subject}")
        
        # Create ticket with 修正 tracker using MCP server
        print("Creating ticket with 修正 tracker via MCP server...")
        
        # Prepare fields for 修正 tracker (ID: 4)
        fields = {
            'issue_description': 'テスト用の修正チケットです。\\n\\n修正内容:\\n- バグの修正\\n- テストケースの追加',
            'issue_assigned_to_id': assignee_id,
            'issue_status_id': '1',  # 新規 status
            'issue_priority_id': '2',  # 通常 priority
            'issue_custom_field_values_3': 'テスト指摘者'  # 指摘者 field
        }
        
        # Add parent ticket if available
        if parent_id:
            fields['issue_parent_issue_id'] = parent_id
        
        create_result = await server.handle_create_issue(
            project_id="hoge-project",
            issue_tracker_id="4",  # 修正 tracker
            issue_subject="修正チケットのテスト - バグ修正 (MCP)",
            fields=fields
        )
        
        if create_result.get('success'):
            issue_id = create_result['issue_id']
            print(f"[OK] Successfully created ticket #{issue_id}")
            print(f"  Subject: 修正チケットのテスト - バグ修正 (MCP)")
            print(f"  Tracker: 修正")
            print(f"  Assignee: {assignee_name} (ID: {assignee_id})")
            print(f"  Reporter (指摘者): テスト指摘者")
            if parent_id:
                print(f"  Parent Issue: #{parent_id}")
            print(f"  URL: {create_result.get('issue_url', 'N/A')}")
            
            # Verify the created ticket
            print("\\nVerifying created ticket...")
            details_result = await server.handle_get_issue_details(issue_id=issue_id)
            if details_result.get('success'):
                issue = details_result['issue']
                print(f"[OK] Verification successful:")
                print(f"  ID: #{issue['id']}")
                print(f"  Subject: {issue['subject']}")
                print(f"  Tracker: {issue['tracker']}")
                print(f"  Status: {issue['status']}")
                print(f"  Assignee: {issue.get('assigned_to', 'Not assigned')}")
                if issue.get('parent'):
                    print(f"  Parent: {issue['parent']}")
                
                # Look for custom fields
                for key, value in issue.items():
                    if '指摘者' in key:
                        print(f"  指摘者: {value}")
            else:
                print(f"Failed to verify ticket: {details_result.get('message')}")
            
            return True
        else:
            print(f"[ERROR] Failed to create ticket: {create_result.get('message')}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")
        return False
    finally:
        # Cleanup
        try:
            await server.handle_logout()
        except:
            pass

if __name__ == "__main__":
    print("=== Test: Create 修正 Ticket via MCP Server ===")
    success = asyncio.run(test_create_修正_ticket_mcp())
    print(f"\\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)