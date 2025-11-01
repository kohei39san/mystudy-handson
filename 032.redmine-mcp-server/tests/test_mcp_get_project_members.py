#!/usr/bin/env python3
"""
Test script for MCP server _handle_get_project_members method
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import asyncio
from redmine_mcp_server import RedmineMCPServer

async def test_mcp_get_project_members():
    """Test MCP server _handle_get_project_members method"""
    
    server = RedmineMCPServer()
    
    try:
        # Login first
        print("Logging in via MCP server...")
        login_result = await server._handle_login({"username": "admin", "password": "admin"})
        print(f"Login result: {login_result[0].text}")
        
        if "[ERROR]" in login_result[0].text:
            return False
        
        # Test get_project_members
        print("\nTesting get_project_members...")
        members_result = await server._handle_get_project_members({"project_id": "hoge-project"})
        
        print("Result:")
        print(members_result[0].text)
        
        # Check if successful
        if "[SUCCESS]" in members_result[0].text:
            print("\n[OK] MCP get_project_members test passed")
            return True
        else:
            print("\n[ERROR] MCP get_project_members test failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")
        return False
    finally:
        try:
            await server._handle_logout({})
        except:
            pass

if __name__ == "__main__":
    print("=== Test: MCP Server _handle_get_project_members ===")
    success = asyncio.run(test_mcp_get_project_members())
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)