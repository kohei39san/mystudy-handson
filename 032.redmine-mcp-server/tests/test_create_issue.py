#!/usr/bin/env python3
"""
Test script for create_issue functionality
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

def test_create_issue():
    """Test create_issue functionality"""
    
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
        
        # Get available trackers
        print("\nGetting available trackers...")
        trackers_result = scraper.get_available_trackers(project_id)
        print(f"Available trackers: {trackers_result}")
        
        if not trackers_result.get('success') or not trackers_result.get('trackers'):
            print("No trackers available for testing")
            return
        
        tracker_id = trackers_result['trackers'][0]['value']
        print(f"Using tracker: {tracker_id}")
        
        # Test 1: Basic issue creation (required fields only)
        print("\n=== Test 1: Basic issue creation ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            subject="Test Issue - Basic Creation",
            tracker_id=int(tracker_id)
        )
        print(f"Create result: {create_result}")
        
        if create_result.get('success'):
            basic_issue_id = create_result.get('issue_id')
            print(f"Created issue #{basic_issue_id}")
        
        # Test 2: Full issue creation (all fields)
        print("\n=== Test 2: Full issue creation ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            subject="Test Issue - Full Creation",
            description="This is a test issue with all fields populated.",
            tracker_id=int(tracker_id),
            priority_id=2,  # Assuming Normal priority
            start_date="2024-01-15",
            due_date="2024-01-30",
            estimated_hours=8.5,
            done_ratio=10
        )
        print(f"Create result: {create_result}")
        
        if create_result.get('success'):
            full_issue_id = create_result.get('issue_id')
            print(f"Created issue #{full_issue_id}")
        
        # Test 3: Invalid tracker validation
        print("\n=== Test 3: Invalid tracker validation ===")
        create_result = scraper.create_issue(
            project_id=project_id,
            subject="Test Issue - Invalid Tracker",
            tracker_id=999  # Invalid tracker ID
        )
        print(f"Create result: {create_result}")
        
        # Test 4: Invalid project validation
        print("\n=== Test 4: Invalid project validation ===")
        create_result = scraper.create_issue(
            project_id="nonexistent-project",
            subject="Test Issue - Invalid Project",
            tracker_id=int(tracker_id)
        )
        print(f"Create result: {create_result}")
        
        # Test 5: Parent issue (if we created issues successfully)
        if 'basic_issue_id' in locals():
            print("\n=== Test 5: Parent issue creation ===")
            create_result = scraper.create_issue(
                project_id=project_id,
                subject="Test Issue - Child Issue",
                tracker_id=int(tracker_id),
                parent_issue_id=int(basic_issue_id)
            )
            print(f"Create result: {create_result}")
        
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
    test_create_issue()