#!/usr/bin/env python3
"""
Test tracker validation functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_tracker_validation():
    """Test tracker validation"""
    
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
        
        # Test valid tracker ID
        print("=== Testing valid tracker ID (4 - 修正) ===")
        validation_result = scraper._validate_tracker_for_project(project_id, "4")
        print(f"Valid: {validation_result['valid']}")
        if not validation_result['valid']:
            print(f"Message: {validation_result['message']}")
        
        # Test invalid tracker ID
        print("\n=== Testing invalid tracker ID (99) ===")
        validation_result = scraper._validate_tracker_for_project(project_id, "99")
        print(f"Valid: {validation_result['valid']}")
        if not validation_result['valid']:
            print(f"Message: {validation_result['message']}")
        
        # Test creating ticket with valid tracker
        print("\n=== Testing ticket creation with tracker ID 4 ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            tracker_id=4,
            subject='テストチケット - トラッカーバリデーション修正後'
        )
        
        if create_result['success']:
            print(f"OK 作成成功: チケット#{create_result['issue_id']}")
            print(f"URL: {create_result['issue_url']}")
        else:
            print(f"NG 作成失敗: {create_result['message']}")
        
    finally:
        scraper.logout()

if __name__ == "__main__":
    test_tracker_validation()