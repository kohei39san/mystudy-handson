#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check issue details to see tracker information
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

async def check_issue_details():
    """Check issue details to see tracker information"""
    print("=== Issue Details Check ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Check details of issue #101
            issue_id = "101"
            print(f"\n--- Getting details for issue #{issue_id} ---")
            details_result = scraper.get_issue_details(issue_id)
            
            if details_result.get('success'):
                issue = details_result['issue']
                print("Issue details:")
                for key, value in issue.items():
                    print(f"  {key}: {value}")
                
                # Check if tracker is available
                if 'tracker' in issue:
                    tracker_name = issue['tracker']
                    print(f"\nFound tracker: '{tracker_name}'")
                    
                    # Test search with this tracker
                    print(f"Testing search with tracker '{tracker_name}'...")
                    search_result = scraper.search_issues(tracker_id=tracker_name, per_page=5)
                    
                    if search_result.get('success'):
                        found_count = search_result.get('total_count', 0)
                        print(f"Search result: {found_count} issues found with tracker '{tracker_name}'")
                        
                        if search_result.get('issues'):
                            print("Sample results:")
                            for i, issue in enumerate(search_result['issues'][:3], 1):
                                print(f"  {i}. #{issue.get('id')} - {issue.get('subject')}")
                    else:
                        print(f"Search failed: {search_result.get('message')}")
                else:
                    print("No tracker information found in issue details")
            else:
                print(f"Failed to get issue details: {details_result.get('message')}")
            
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
    asyncio.run(check_issue_details())