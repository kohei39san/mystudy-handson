#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def main():
    redmine = RedmineSeleniumScraper()
    
    # Login
    print("Logging in...")
    login_result = redmine.login("admin", "admin")
    if not login_result['success']:
        print(f"Login failed: {login_result['message']}")
        return
    
    print("Login successful!")
    
    # Test 1: Valid fields for 修正 tracker
    print("\n=== Test 1: Valid fields for 修正 tracker ===")
    valid_fields = {
        'issue_tracker_id': '4',
        'issue_subject': 'Test Subject',
        'issue_status_id': '1',
        'issue_priority_id': '2',
        'issue_assigned_to_id': '1',
        'issue_custom_field_values_3': '1'
    }
    
    validation_result = redmine._validate_fields("hoge-project", "4", valid_fields)
    print(f"Result: {validation_result}")
    
    # Test 2: Missing required fields
    print("\n=== Test 2: Missing required fields ===")
    missing_required = {
        'issue_tracker_id': '4',
        'issue_subject': 'Test Subject'
        # Missing status_id and priority_id
    }
    
    validation_result = redmine._validate_fields("hoge-project", "4", missing_required)
    print(f"Result: {validation_result}")
    
    # Test 3: Invalid field names
    print("\n=== Test 3: Invalid field names ===")
    invalid_fields = {
        'issue_tracker_id': '4',
        'issue_subject': 'Test Subject',
        'issue_status_id': '1',
        'issue_priority_id': '2',
        'invalid_field': 'some value',
        'another_invalid': 'another value'
    }
    
    validation_result = redmine._validate_fields("hoge-project", "4", invalid_fields)
    print(f"Result: {validation_result}")
    
    # Test 4: Invalid assignee
    print("\n=== Test 4: Invalid assignee ===")
    invalid_assignee = {
        'issue_tracker_id': '4',
        'issue_subject': 'Test Subject',
        'issue_status_id': '1',
        'issue_priority_id': '2',
        'issue_assigned_to_id': '999'  # Non-existent user
    }
    
    validation_result = redmine._validate_fields("hoge-project", "4", invalid_assignee)
    print(f"Result: {validation_result}")
    
    # Test 5: Default tracker (no custom fields)
    print("\n=== Test 5: Default tracker validation ===")
    default_fields = {
        'issue_subject': 'Test Subject',
        'issue_status_id': '1',
        'issue_priority_id': '2',
        'issue_custom_field_values_3': '1'  # Should be invalid for default tracker
    }
    
    validation_result = redmine._validate_fields("hoge-project", "1", default_fields)
    print(f"Result: {validation_result}")
    
    # Logout
    redmine.logout()
    print("\nLogged out.")

if __name__ == "__main__":
    main()