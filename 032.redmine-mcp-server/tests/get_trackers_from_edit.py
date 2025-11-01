#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get available trackers from issue edit page
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

async def get_trackers_from_edit():
    """Get available trackers from issue edit page"""
    print("=== Get Trackers from Edit Page ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Navigate to issue edit page to get tracker options
            issue_id = "101"
            edit_url = f"{config.base_url}/issues/{issue_id}/edit"
            print(f"\nNavigating to edit page: {edit_url}")
            
            scraper.driver.get(edit_url)
            
            # Wait for page to load
            import time
            time.sleep(3)
            
            # Get tracker options
            try:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import Select
                
                tracker_select = scraper.driver.find_element(By.ID, "issue_tracker_id")
                select = Select(tracker_select)
                
                print("Available trackers:")
                trackers = []
                for option in select.options:
                    value = option.get_attribute('value')
                    text = option.text.strip()
                    if value:  # Skip empty values
                        trackers.append({
                            'value': value,
                            'text': text
                        })
                        print(f"  - {text} (ID: {value})")
                
                # Test search with each tracker
                if trackers:
                    print(f"\n--- Testing search with each tracker ---")
                    for tracker in trackers:
                        print(f"\nTesting tracker ID '{tracker['value']}' ({tracker['text']}):")
                        
                        # Test with ID
                        search_result = scraper.search_issues(tracker_id=tracker['value'], per_page=5)
                        if search_result.get('success'):
                            count = search_result.get('total_count', 0)
                            print(f"  By ID: {count} issues found")
                        
                        # Test with name
                        search_result = scraper.search_issues(tracker_id=tracker['text'], per_page=5)
                        if search_result.get('success'):
                            count = search_result.get('total_count', 0)
                            print(f"  By name: {count} issues found")
                
            except Exception as e:
                print(f"Error getting tracker options: {e}")
            
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
    asyncio.run(get_trackers_from_edit())