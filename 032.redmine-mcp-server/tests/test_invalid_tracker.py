#!/usr/bin/env python3
"""
Test invalid tracker ID handling in ticket creation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_invalid_tracker():
    """Test invalid tracker ID handling"""
    
    # Get credentials from environment
    username = os.getenv('REDMINE_USERNAME')
    password = os.getenv('REDMINE_PASSWORD')
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        login_result = scraper.login(username, password)
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return
        
        project_id = 'hoge-project'
        
        # Test 1: Valid tracker ID (should succeed)
        print("=== Test 1: Valid tracker ID (4 - 修正) ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            tracker_id=4,
            subject='テストチケット - 有効なトラッカー'
        )
        
        if create_result['success']:
            print(f"OK 作成成功: チケット#{create_result['issue_id']}")
        else:
            print(f"NG 作成失敗: {create_result['message']}")
        
        # Test 2: Invalid tracker ID (should fail)
        print("\n=== Test 2: Invalid tracker ID (99) ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            tracker_id=99,
            subject='テストチケット - 無効なトラッカー'
        )
        
        if create_result['success']:
            print(f"NG 予期しない成功: チケット#{create_result['issue_id']}")
        else:
            print(f"OK 期待通りの失敗: {create_result['message']}")
        
        # Test 3: Non-existent tracker ID (should fail)
        print("\n=== Test 3: Non-existent tracker ID (999) ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            tracker_id=999,
            subject='テストチケット - 存在しないトラッカー'
        )
        
        if create_result['success']:
            print(f"NG 予期しない成功: チケット#{create_result['issue_id']}")
        else:
            print(f"OK 期待通りの失敗: {create_result['message']}")
        
    finally:
        scraper.logout()

if __name__ == "__main__":
    test_invalid_tracker()