#!/usr/bin/env python3
"""
Debug test for subject field issue
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

def test_debug_subject():
    """Debug subject field issue"""
    
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
        
        # Test create issue with minimal parameters
        print("\n=== デバッグ: チケット作成 ===")
        create_result = scraper.create_issue(
            project_id="hoge-project",
            subject="デバッグテスト",
            tracker_id=1
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
    test_debug_subject()