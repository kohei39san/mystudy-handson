#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check what trackers exist in the system
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

async def check_trackers():
    """Check existing trackers in the system"""
    print("=== Tracker Check ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Get all issues to see what trackers exist
            print("\n--- Getting all issues to check trackers ---")
            search_result = scraper.search_issues(per_page=25)
            
            if search_result.get('success'):
                issues = search_result.get('issues', [])
                total_count = search_result.get('total_count', 0)
                print(f"Found {total_count} total issues")
                
                # Collect unique trackers
                trackers = set()
                for issue in issues:
                    if issue.get('tracker'):
                        trackers.add(issue['tracker'])
                
                print(f"\nFound trackers in existing issues:")
                for tracker in sorted(trackers):
                    print(f"  - {tracker}")
                
                # Show some sample issues with their trackers
                print(f"\nSample issues with tracker info:")
                for i, issue in enumerate(issues[:5], 1):
                    print(f"  {i}. #{issue.get('id')} - {issue.get('subject', 'No subject')}")
                    print(f"     Tracker: {issue.get('tracker', 'Unknown')}")
                    print(f"     Status: {issue.get('status', 'Unknown')}")
                    print()
                
                # Test search with actual tracker names found
                if trackers:
                    print("--- Testing search with found tracker names ---")
                    for tracker in sorted(trackers):
                        print(f"\nSearching for tracker: '{tracker}'")
                        tracker_search = scraper.search_issues(tracker_id=tracker, per_page=5)
                        if tracker_search.get('success'):
                            found_count = tracker_search.get('total_count', 0)
                            print(f"  Result: {found_count} issues found")
                        else:
                            print(f"  Error: {tracker_search.get('message')}")
            else:
                print(f"Failed to get issues: {search_result.get('message')}")
            
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
    asyncio.run(check_trackers())