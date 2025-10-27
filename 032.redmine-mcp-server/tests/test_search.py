#!/usr/bin/env python3
"""
Test script for search_issues functionality
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

# Load environment variables
load_dotenv()

# Set up logging to see debug output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_search_issues():
    """Test search_issues with tracker_id=1"""
    
    # Get credentials from environment with defaults
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    
    print(f"Using credentials: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login(username, password)
        print(f"Login result: {login_result}")
        
        if not login_result.get('success'):
            print("Login failed, cannot proceed with test")
            return
        
        # Test search with tracker_id=1
        print("\nTesting search with tracker_id=1...")
        search_result = scraper.search_issues(tracker_id="1")
        
        print(f"Search result: {search_result}")
        print(f"Number of issues found: {len(search_result.get('issues', []))}")
        
        # Test search without filters to see if any issues exist
        print("\nTesting search without filters...")
        search_all_result = scraper.search_issues()
        
        print(f"Search all result: {search_all_result}")
        print(f"Total issues without filter: {len(search_all_result.get('issues', []))}")
        
        # Get available trackers
        print("\nGetting available trackers...")
        trackers_result = scraper.get_available_trackers()
        print(f"Available trackers: {trackers_result}")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Logout
        print("\nLogging out...")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    test_search_issues()