#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to update issue #101 status to "In Progress" (status_id=2)
"""

import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
from config import config

async def simple_status_update():
    """Simple test to update status"""
    print("=== Simple Status Update Test ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Update status to "In Progress" (commonly status_id=2)
            print("Updating issue #101 status to 'In Progress' (status_id=2)...")
            
            update_result = scraper.update_issue(
                "101", 
                status_id="2",
                notes="Status changed to In Progress via MCP test"
            )
            
            print(f"Update result: {json.dumps(update_result, indent=2)}")
            
            if update_result.get('success'):
                print("[OK] Update successful!")
                print(f"Updated fields: {update_result.get('updated_fields', [])}")
            else:
                print("[FAIL] Update failed")
                print(f"Error: {update_result.get('message')}")
            
            # Logout
            scraper.logout()
            print("[OK] Logged out")
        else:
            print("[FAIL] Login failed")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.logout()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(simple_status_update())