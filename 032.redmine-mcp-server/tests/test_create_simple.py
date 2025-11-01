#!/usr/bin/env python3
"""
Simple test for create_issue functionality
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

def test_create_simple():
    """Simple test for create_issue functionality"""
    
    # Get credentials from environment with defaults
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    
    print(f"Using credentials: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login(username, password)
        print(f"Login result: {login_result}")
        
        if not login_result.get('success'):
            print("Login failed, cannot proceed with test")
            return
        
        # Get projects first
        print("\nGetting projects...")
        projects_result = scraper.get_projects()
        if not projects_result.get('success') or not projects_result.get('projects'):
            print("No projects available for testing")
            return
        
        project_id = projects_result['projects'][0]['id']
        print(f"Using project: {project_id}")
        
        # Get available trackers (without project_id to get global trackers)
        print("\nGetting available trackers...")
        trackers_result = scraper.get_available_trackers()
        print(f"Available trackers: {trackers_result}")
        
        if not trackers_result.get('success') or not trackers_result.get('trackers'):
            print("No trackers available, trying with default tracker ID 1")
            tracker_id = "1"
        else:
            tracker_id = trackers_result['trackers'][0]['value']
        
        print(f"Using tracker: {tracker_id}")
        
        # Test: Basic issue creation
        print("\n=== Test: Basic issue creation ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            subject="Test Issue - Simple Creation",
            tracker_id=int(tracker_id)
        )
        print(f"Create result: {create_result}")
        
        if create_result.get('success'):
            issue_id = create_result.get('issue_id')
            print(f"Successfully created issue #{issue_id}")
            print(f"Issue URL: {create_result.get('issue_url')}")
        else:
            print(f"Failed to create issue: {create_result.get('message')}")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Logout
        print("\nLogging out...")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    test_create_simple()