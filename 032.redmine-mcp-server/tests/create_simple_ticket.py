#!/usr/bin/env python3
"""
Create a simple ticket without validation to test basic functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def create_simple_ticket():
    """Create a simple ticket"""
    
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
        
        # Create ticket with minimal parameters
        create_result = scraper.create_issue(
            project_id='hoge-project',
            subject='テストチケット - 修正トラッカー'
        )
        
        if create_result['success']:
            print(f"OK 作成成功: チケット#{create_result['issue_id']}")
            print(f"URL: {create_result['issue_url']}")
        else:
            print(f"NG 作成失敗: {create_result['message']}")
        
    finally:
        scraper.logout()

if __name__ == "__main__":
    create_simple_ticket()