#!/usr/bin/env python3
"""
Test script to check issue details functionality
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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_issue_details():
    """Test get_issue_details functionality"""
    
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    
    print(f"Using credentials: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("=== ログイン ===")
        login_result = scraper.login(username, password)
        if not login_result.get('success'):
            print("Login failed")
            return
        
        # Test with recently created issues
        issue_ids = ["105", "106", "107"]
        
        for issue_id in issue_ids:
            print(f"\n=== チケット#{issue_id}の詳細取得 ===")
            details_result = scraper.get_issue_details(issue_id)
            print(f"Details result: {details_result}")
            
            if details_result.get('success'):
                issue = details_result['issue']
                print(f"ID: {issue.get('id', 'Unknown')}")
                print(f"Subject: {issue.get('subject', 'Unknown')}")
                print(f"Status: {issue.get('status', 'Unknown')}")
                print(f"Priority: {issue.get('priority', 'Unknown')}")
                print(f"Tracker: {issue.get('tracker', 'Unknown')}")
                print(f"Assignee: {issue.get('assignee', 'Unknown')}")
                print(f"Description: {issue.get('description', 'Unknown')}")
                print(f"Created: {issue.get('created_on', 'Unknown')}")
                print(f"Updated: {issue.get('updated_on', 'Unknown')}")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Logout
        print("\n=== ログアウト ===")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    test_issue_details()