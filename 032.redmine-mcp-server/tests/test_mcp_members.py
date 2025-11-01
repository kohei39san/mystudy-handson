#!/usr/bin/env python3
"""
Test script for MCP server get_project_members tool
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

async def test_mcp_project_members():
    """Test MCP server get_project_members tool"""
    
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    
    print(f"Testing MCP server with credentials: {username}/{password}")
    
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
        
        # Test get projects
        print("\n=== MCP Get Projects Test ===")
        projects_result = await mcp_server._handle_get_projects({})
        print(f"Projects result: {projects_result[0].text}")
        
        # Test get project members for hoge-project
        print("\n=== MCP Get Project Members Test (hoge-project) ===")
        members_result = await mcp_server._handle_get_project_members({
            "project_id": "hoge-project"
        })
        print(f"Members result: {members_result[0].text}")
        
        # Test get project members for fuga-project
        print("\n=== MCP Get Project Members Test (fuga-project) ===")
        members_result2 = await mcp_server._handle_get_project_members({
            "project_id": "fuga-project"
        })
        print(f"Members result: {members_result2[0].text}")
        
        # Test invalid project
        print("\n=== MCP Get Project Members Test (invalid project) ===")
        invalid_result = await mcp_server._handle_get_project_members({
            "project_id": "nonexistent-project"
        })
        print(f"Invalid project result: {invalid_result[0].text}")
        
        # Test missing project_id
        print("\n=== MCP Get Project Members Test (missing project_id) ===")
        missing_result = await mcp_server._handle_get_project_members({})
        print(f"Missing project_id result: {missing_result[0].text}")
        
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
    asyncio.run(test_mcp_project_members())