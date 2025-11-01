#!/usr/bin/env python3
"""
Test script to verify all fields are returned by get_issue_details
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_all_fields():
    """Test that get_issue_details returns all available fields"""
    
    # Get credentials from environment
    username = os.getenv('REDMINE_USERNAME')
    password = os.getenv('REDMINE_PASSWORD')
    
    if not username or not password:
        print("Error: REDMINE_USERNAME and REDMINE_PASSWORD must be set in .env file")
        return
    
    print(f"Using credentials: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("=== ログイン ===")
        login_result = scraper.login(username, password)
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return
        
        # Test with issue #118 (newly created)
        issue_id = "118"
        print(f"\n=== チケット#{issue_id}の全フィールド取得テスト ===")
        
        details_result = scraper.get_issue_details(issue_id)
        
        if details_result['success']:
            issue = details_result['issue']
            print(f"取得されたフィールド数: {len(issue)}")
            print("\n全フィールド:")
            for key, value in issue.items():
                print(f"  {key}: {value}")
        else:
            print(f"Failed: {details_result['message']}")
        
        # Test with issue #106 (has more fields)
        issue_id = "106"
        print(f"\n=== チケット#{issue_id}の全フィールド取得テスト ===")
        
        details_result = scraper.get_issue_details(issue_id)
        
        if details_result['success']:
            issue = details_result['issue']
            print(f"取得されたフィールド数: {len(issue)}")
            print("\n全フィールド:")
            for key, value in issue.items():
                print(f"  {key}: {value}")
        else:
            print(f"Failed: {details_result['message']}")
        
    finally:
        # Logout
        print("\n=== ログアウト ===")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    test_all_fields()