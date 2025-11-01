#!/usr/bin/env python3
"""
Check available trackers for the project
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def check_trackers():
    """Check available trackers"""
    
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
        
        # Get available trackers
        project_id = 'hoge-project'
        trackers_result = scraper.get_available_trackers(project_id)
        
        if trackers_result['success']:
            print(f"Available trackers for project {project_id}:")
            for tracker in trackers_result['trackers']:
                print(f"  ID: {tracker['value']} - Name: {tracker['text']}")
        else:
            print(f"Failed to get trackers: {trackers_result['message']}")
        
    finally:
        scraper.logout()

if __name__ == "__main__":
    check_trackers()