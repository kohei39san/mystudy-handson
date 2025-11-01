#!/usr/bin/env python3
"""
Test script to verify complete _validate_fields integration in create_issue method
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
import config

def test_create_issue_full_validation():
    """Test create_issue with complete field validation"""
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        username = os.getenv('REDMINE_USERNAME', 'kohei')
        password = os.getenv('REDMINE_PASSWORD', 'ariari_ssKK3')
        login_result = scraper.login(username, password)
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return
        print("Login successful")
        
        project_id = "hoge-project"
        tracker_id = "4"  # 修正 tracker
        
        print("\n=== Test 1: Complete valid fields ===")
        complete_valid_fields = {
            'issue_subject': 'Test Issue with Complete Validation',
            'issue_description': 'Test description',
            'issue_status_id': '1',  # New
            'issue_priority_id': '2',  # Normal
            'issue_assigned_to_id': '1',  # admin user
            'issue_custom_field_values_3': '1'  # 指摘者 field
        }
        
        result = scraper.create_issue(project_id, tracker_id, **complete_valid_fields)
        print(f"Complete valid fields result: {result}")
        
        print("\n=== Test 2: Invalid assignee with all required fields ===")
        invalid_assignee_complete = {
            'issue_subject': 'Test Issue with Invalid Assignee',
            'issue_description': 'Test description',
            'issue_status_id': '1',
            'issue_priority_id': '2',
            'issue_assigned_to_id': '999',  # Non-existent user
            'issue_custom_field_values_3': '1'
        }
        
        result = scraper.create_issue(project_id, tracker_id, **invalid_assignee_complete)
        print(f"Invalid assignee result: {result}")
        
        print("\n=== Test 3: Invalid field name with all required fields ===")
        invalid_field_complete = {
            'issue_subject': 'Test Issue with Invalid Field',
            'issue_status_id': '1',
            'issue_priority_id': '2',
            'issue_assigned_to_id': '1',
            'invalid_field_name': 'some value'  # Invalid field
        }
        
        result = scraper.create_issue(project_id, tracker_id, **invalid_field_complete)
        print(f"Invalid field name result: {result}")
        
        print("\n=== Test 4: Custom field in wrong tracker ===")
        wrong_tracker_complete = {
            'issue_subject': 'Test Issue in Wrong Tracker',
            'issue_status_id': '1',
            'issue_priority_id': '2',
            'issue_assigned_to_id': '1',
            'issue_custom_field_values_3': '1'  # This field only exists in tracker 4
        }
        
        result = scraper.create_issue(project_id, "1", **wrong_tracker_complete)  # Using tracker 1 (課題)
        print(f"Wrong tracker for custom field result: {result}")
        
        print("\n=== Test 5: Minimal valid fields (only required) ===")
        minimal_valid_fields = {
            'issue_subject': 'Minimal Test Issue',
            'issue_status_id': '1',
            'issue_priority_id': '2'
        }
        
        result = scraper.create_issue(project_id, tracker_id, **minimal_valid_fields)
        print(f"Minimal valid fields result: {result}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    test_create_issue_full_validation()