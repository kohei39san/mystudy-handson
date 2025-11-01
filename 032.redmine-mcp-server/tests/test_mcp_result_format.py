#!/usr/bin/env python3
"""
Test MCP server result format - verify that handlers return full result objects
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_mcp_server import RedmineMCPServer

async def test_result_format():
    """Test that MCP server handlers return full result objects as JSON"""
    
    server = RedmineMCPServer()
    
    # Test get_server_info (doesn't require authentication)
    print("Testing get_server_info result format...")
    result = await server._handle_get_server_info({})
    
    # Should return TextContent with text field
    assert len(result) == 1
    assert result[0].type == "text"
    
    # The text should be server info, not JSON (this method is special)
    text = result[0].text
    print(f"Server info result: {text[:100]}...")
    assert "Redmine Server Information" in text
    
    # Test get_projects (requires authentication, should return error)
    print("\nTesting get_projects result format (unauthenticated)...")
    result = await server._handle_get_projects({})
    
    assert len(result) == 1
    assert result[0].type == "text"
    
    # Should be error message for unauthenticated access
    text = result[0].text
    print(f"Get projects result: {text}")
    assert "Not authenticated" in text
    
    # Test login with invalid credentials
    print("\nTesting login result format...")
    result = await server._handle_login({"username": "test", "password": "invalid"})
    
    assert len(result) == 1
    assert result[0].type == "text"
    
    # Should be Python dict format
    text = result[0].text
    print(f"Login result: {text}")
    
    try:
        # Use eval to parse Python dict format (safe since we control the input)
        parsed = eval(text)
        assert "success" in parsed
        assert "message" in parsed
        print("[OK] Login result is valid dict with success and message fields")
    except (SyntaxError, NameError) as e:
        print(f"[ERROR] Login result is not valid Python dict: {e}")
        raise
    
    print("\n[OK] All result format tests passed!")

if __name__ == "__main__":
    asyncio.run(test_result_format())