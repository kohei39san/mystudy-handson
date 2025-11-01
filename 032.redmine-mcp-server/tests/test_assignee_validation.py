#!/usr/bin/env python3
"""
Test script for assignee validation functionality
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

def test_assignee_validation():
    """Test assignee validation functionality"""
    
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
        
        project_id = "hoge-project"
        tracker_id = "1"
        
        # Get project members first
        print(f"\n=== プロジェクト {project_id} のメンバー取得 ===")
        members_result = scraper.get_project_members(project_id)
        if members_result.get('success'):
            members = members_result.get('members', [])
            print(f"Available members:")
            for member in members:
                print(f"  - {member.get('name')} (ID: {member.get('id')})")
        
        # Test 1: Valid assignee by ID
        print(f"\n=== Test 1: 有効な担当者ID (1) ===")
        fields = {'assigned_to_id': '1'}
        validation_result = scraper._validate_fields(project_id, tracker_id, fields)
        print(f"Validation result: {validation_result}")
        
        # Test 2: Valid assignee by name
        print(f"\n=== Test 2: 有効な担当者名 (Redmine Admin) ===")
        fields = {'assigned_to_id': 'Redmine Admin'}
        validation_result = scraper._validate_fields(project_id, tracker_id, fields)
        print(f"Validation result: {validation_result}")
        
        # Test 3: Invalid assignee ID
        print(f"\n=== Test 3: 無効な担当者ID (999) ===")
        fields = {'assigned_to_id': '999'}
        validation_result = scraper._validate_fields(project_id, tracker_id, fields)
        print(f"Validation result: {validation_result}")
        
        # Test 4: Invalid assignee name
        print(f"\n=== Test 4: 無効な担当者名 (NonExistentUser) ===")
        fields = {'assigned_to_id': 'NonExistentUser'}
        validation_result = scraper._validate_fields(project_id, tracker_id, fields)
        print(f"Validation result: {validation_result}")
        
        # Test 5: Special value 'me'
        print(f"\n=== Test 5: 特別な値 'me' ===")
        fields = {'assigned_to_id': 'me'}
        validation_result = scraper._validate_fields(project_id, tracker_id, fields)
        print(f"Validation result: {validation_result}")
        
        # Test 6: Empty assignee
        print(f"\n=== Test 6: 空の担当者 ===")
        fields = {'assigned_to_id': ''}
        validation_result = scraper._validate_fields(project_id, tracker_id, fields)
        print(f"Validation result: {validation_result}")
        
        # Test 7: Create issue with valid assignee
        print(f"\n=== Test 7: 有効な担当者でチケット作成 ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            subject="担当者バリデーションテスト - 有効",
            tracker_id=int(tracker_id),
            assigned_to_id='1'
        )
        print(f"Create result: {create_result}")
        
        # Test 8: Create issue with invalid assignee
        print(f"\n=== Test 8: 無効な担当者でチケット作成 ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            subject="担当者バリデーションテスト - 無効",
            tracker_id=int(tracker_id),
            assigned_to_id='999'
        )
        print(f"Create result: {create_result}")
        
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
    test_assignee_validation()