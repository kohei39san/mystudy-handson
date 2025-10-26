#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for tracker search functionality
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

async def test_tracker_search():
    """Test searching issues by tracker"""
    print("=== Tracker Search Test ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Test tracker search with different values
            tracker_tests = [
                "課題",           # Japanese name
                "Bug",            # English name  
                "Feature",        # English name
                "Task",           # English name
                "1",              # ID
                "2",              # ID
                "3"               # ID
            ]
            
            for tracker in tracker_tests:
                print(f"\n--- Testing tracker: '{tracker}' ---")
                search_result = scraper.search_issues(tracker_id=tracker, per_page=5)
                
                if search_result.get('success'):
                    issues = search_result.get('issues', [])
                    total_count = search_result.get('total_count', 0)
                    print(f"Found {total_count} issues with tracker '{tracker}'")
                    
                    if issues:
                        print("Sample issues:")
                        for i, issue in enumerate(issues[:3], 1):  # Show first 3
                            print(f"  {i}. #{issue.get('id')} - {issue.get('subject', 'No subject')}")
                            if issue.get('tracker'):
                                print(f"     Tracker: {issue['tracker']}")
                    else:
                        print("No issues found for this tracker")
                else:
                    print(f"Search failed: {search_result.get('message')}")
            
            # Logout
            scraper.logout()
            print("\n[OK] Logged out")
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
    asyncio.run(test_tracker_search())