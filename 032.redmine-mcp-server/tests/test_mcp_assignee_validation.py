#!/usr/bin/env python3
"""
Test script for MCP server assignee validation
"""

import asyncio
import json
import sys
import os
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_mcp_server import RedmineMCPServer

# Load environment variables
load_dotenv()

async def test_mcp_assignee_validation():
    """Test MCP server assignee validation"""
    
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    
    print(f"Testing MCP server assignee validation with credentials: {username}/{password}")
    
    # Create MCP server instance
    mcp_server = RedmineMCPServer()
    
    try:
        # Test login
        print("\n=== MCP Login Test ===")
        login_result = await mcp_server._handle_login({
            "username": username,
            "password": password
        })
        print(f"Login result: {login_result[0].text}")
        
        if "[ERROR]" in login_result[0].text:
            print("Login failed, cannot proceed")
            return
        
        # Test get project members
        print("\n=== MCP Get Project Members Test ===")
        members_result = await mcp_server._handle_get_project_members({
            "project_id": "hoge-project"
        })
        print(f"Members result: {members_result[0].text}")
        
        # Test create issue with valid assignee
        print("\n=== MCP Create Issue with Valid Assignee ===")
        create_result = await mcp_server._handle_create_issue({
            "project_id": "hoge-project",
            "subject": "MCP担当者バリデーションテスト - 有効",
            "tracker_id": 1,
            "fields": {
                "assigned_to_id": "1"
            }
        })
        print(f"Create result: {create_result[0].text}")
        
        # Test create issue with invalid assignee
        print("\n=== MCP Create Issue with Invalid Assignee ===")
        create_result2 = await mcp_server._handle_create_issue({
            "project_id": "hoge-project",
            "subject": "MCP担当者バリデーションテスト - 無効",
            "tracker_id": 1,
            "fields": {
                "assigned_to_id": "999"
            }
        })
        print(f"Create result: {create_result2[0].text}")
        
        # Test create issue with assignee by name
        print("\n=== MCP Create Issue with Assignee by Name ===")
        create_result3 = await mcp_server._handle_create_issue({
            "project_id": "hoge-project",
            "subject": "MCP担当者バリデーションテスト - 名前指定",
            "tracker_id": 1,
            "fields": {
                "assigned_to_id": "Redmine Admin"
            }
        })
        print(f"Create result: {create_result3[0].text}")
        
        # Test create issue with 'me' assignee
        print("\n=== MCP Create Issue with 'me' Assignee ===")
        create_result4 = await mcp_server._handle_create_issue({
            "project_id": "hoge-project",
            "subject": "MCP担当者バリデーションテスト - me指定",
            "tracker_id": 1,
            "fields": {
                "assigned_to_id": "me"
            }
        })
        print(f"Create result: {create_result4[0].text}")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Test logout
        print("\n=== MCP Logout Test ===")
        logout_result = await mcp_server._handle_logout({})
        print(f"Logout result: {logout_result[0].text}")

if __name__ == "__main__":
    asyncio.run(test_mcp_assignee_validation())