#!/usr/bin/env python3
"""
Test script to verify _validate_fields integration in create_issue method
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
import config

def test_create_issue_validation():
    """Test create_issue with field validation"""
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
        
        print("\n=== Test 1: Valid fields ===")
        valid_fields = {
            'issue_subject': 'Test Issue with Validation',
            'issue_description': 'Test description',
            'issue_assigned_to_id': '1',  # admin user
            'issue_custom_field_values_3': '1'  # 指摘者 field
        }
        
        result = scraper.create_issue(project_id, tracker_id, **valid_fields)
        print(f"Valid fields result: {result}")
        
        print("\n=== Test 2: Missing required field (subject) ===")
        missing_subject = {
            'issue_description': 'Test description without subject',
            'issue_assigned_to_id': '1',
            'issue_custom_field_values_3': '1'
        }
        
        result = scraper.create_issue(project_id, tracker_id, **missing_subject)
        print(f"Missing subject result: {result}")
        
        print("\n=== Test 3: Invalid field name ===")
        invalid_field = {
            'issue_subject': 'Test Issue',
            'invalid_field_name': 'some value',
            'issue_assigned_to_id': '1'
        }
        
        result = scraper.create_issue(project_id, tracker_id, **invalid_field)
        print(f"Invalid field result: {result}")
        
        print("\n=== Test 4: Invalid assignee ===")
        invalid_assignee = {
            'issue_subject': 'Test Issue',
            'issue_assigned_to_id': '999',  # Non-existent user
            'issue_custom_field_values_3': '1'
        }
        
        result = scraper.create_issue(project_id, tracker_id, **invalid_assignee)
        print(f"Invalid assignee result: {result}")
        
        print("\n=== Test 5: Wrong tracker for custom field ===")
        wrong_tracker_fields = {
            'issue_subject': 'Test Issue',
            'issue_custom_field_values_3': '1'  # This field only exists in tracker 4
        }
        
        result = scraper.create_issue(project_id, "1", **wrong_tracker_fields)  # Using tracker 1 (課題)
        print(f"Wrong tracker result: {result}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    test_create_issue_validation()