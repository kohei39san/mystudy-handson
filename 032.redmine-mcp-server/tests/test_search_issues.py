#!/usr/bin/env python3
"""
Test script for search_issues with updated table selector
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_search_issues():
    """Test search_issues with updated table selector"""
    
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
        
        # Test search issues
        print("\n=== チケット検索テスト ===")
        search_result = scraper.search_issues(project_id='hoge-project')
        
        print(f"Search success: {search_result['success']}")
        print(f"Message: {search_result['message']}")
        print(f"Total count: {search_result['total_count']}")
        print(f"Issues found: {len(search_result['issues'])}")
        
        # Show first few issues
        for i, issue in enumerate(search_result['issues'][:5]):
            print(f"  Issue #{issue['id']}: {issue.get('subject', 'No subject')}")
        
    finally:
        # Logout
        print("\n=== ログアウト ===")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    test_search_issues()