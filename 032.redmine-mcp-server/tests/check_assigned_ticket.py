#!/usr/bin/env python3
"""
Check the details of the created assigned ticket
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def check_assigned_ticket():
    """Check the details of the assigned ticket"""
    
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
        
        # Check ticket #131 details
        issue_id = "131"
        print(f"=== チケット#{issue_id}の詳細確認 ===")
        
        details_result = scraper.get_issue_details(issue_id)
        
        if details_result['success']:
            issue = details_result['issue']
            print(f"ID: {issue['id']}")
            print(f"Subject: {issue.get('subject', 'Unknown')}")
            print(f"Tracker: {issue.get('tracker', 'Unknown')}")
            print(f"Status: {issue.get('status', 'Unknown')}")
            print(f"Priority: {issue.get('priority', 'Unknown')}")
            print(f"Assigned to (担当者): {issue.get('担当者', 'Unknown')}")
            print(f"Description: {issue.get('description', 'Unknown')}")
            
            print(f"\n全フィールド ({len(issue)} 個):")
            for key, value in issue.items():
                print(f"  {key}: {value}")
                
        else:
            print(f"詳細取得失敗: {details_result['message']}")
        
    finally:
        scraper.logout()

if __name__ == "__main__":
    check_assigned_ticket()