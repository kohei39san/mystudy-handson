#!/usr/bin/env python3
"""
Test script for Redmine MCP Server
This script can be used to test the scraper functionality independently
"""

import sys
import os
import asyncio
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from redmine_scraper import RedmineScraper
from config import config

async def test_scraper():
    """Test the Redmine scraper functionality"""
    print(f"🔧 Testing Redmine MCP Server")
    print(f"Target URL: {config.base_url}")
    print("=" * 50)
    
    scraper = RedmineScraper()
    
    # Test server info
    print("\n📋 Server Configuration:")
    print(f"  Base URL: {config.base_url}")
    print(f"  Login URL: {config.login_url}")
    print(f"  Projects URL: {config.projects_url}")
    print(f"  Session Timeout: {config.session_timeout}s")
    print(f"  Request Timeout: {config.request_timeout}s")
    
    # Get credentials from user
    print("\n🔐 Authentication Test:")
    username = input("Enter Redmine username (or 'skip' to skip auth test): ")
    
    if username.lower() != 'skip':
        password = input("Enter Redmine password: ")
        
        print(f"\n🚀 Attempting login...")
        login_result = scraper.login(username, password)
        
        print(f"Login Result: {json.dumps(login_result, indent=2)}")
        
        if login_result['success']:
            print("\n📂 Fetching projects...")
            projects_result = scraper.get_projects()
            
            print(f"Projects Result: {json.dumps(projects_result, indent=2)}")
            
            print("\n🚪 Logging out...")
            logout_result = scraper.logout()
            print(f"Logout Result: {json.dumps(logout_result, indent=2)}")
        else:
            print("❌ Login failed, skipping project fetch test")
    else:
        print("⏭️  Skipping authentication test")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    try:
        asyncio.run(test_scraper())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1)