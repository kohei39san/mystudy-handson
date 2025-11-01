#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
import time

def main():
    redmine = RedmineSeleniumScraper()
    
    # Login
    print("Logging in...")
    login_result = redmine.login("admin", "admin")
    if not login_result['success']:
        print(f"Login failed: {login_result['message']}")
        return
    
    print("Login successful!")
    
    # Create simple ticket with just required fields
    print("Creating simple ticket...")
    
    create_result = redmine.create_issue(
        project_id="hoge-project",
        subject="Simple Test Ticket",
        issue_tracker_id="4",  # 修正 tracker
        issue_subject="Simple Test Ticket",
        issue_status_id="1",  # New status
        issue_priority_id="2"  # Normal priority
    )
    
    if create_result['success']:
        print(f"[SUCCESS] Successfully created ticket: {create_result['message']}")
        print(f"  Issue ID: {create_result['issue_id']}")
        print(f"  Issue URL: {create_result['issue_url']}")
    else:
        print(f"[ERROR] Failed to create ticket: {create_result['message']}")
    
    # Logout
    redmine.logout()
    print("Logged out.")

if __name__ == "__main__":
    main()