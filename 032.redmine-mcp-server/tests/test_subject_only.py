#!/usr/bin/env python3
"""
Test script to specifically test the subject field functionality
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from redmine_selenium import RedmineSeleniumScraper

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_subject_field():
    """Test subject field functionality specifically"""
    
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
        
        # Use hoge-project which has members
        project_id = "hoge-project"
        
        # Test: Basic issue creation with minimal fields
        print(f"\n=== Test: Subject field with project {project_id} ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            subject="Test Subject Field - Minimal Creation"
        )
        print(f"Create result: {create_result}")
        
        if create_result.get('success'):
            issue_id = create_result.get('issue_id')
            print(f"✅ Successfully created issue #{issue_id}")
            print(f"Issue URL: {create_result.get('issue_url')}")
        else:
            print(f"❌ Failed to create issue: {create_result.get('message')}")
        
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
    test_subject_field()