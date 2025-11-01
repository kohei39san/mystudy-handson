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
    
    # Test get_tracker_fields with URL parameter
    print("Testing get_tracker_fields with tracker_id=4 (修正)...")
    
    start_time = time.time()
    fields_result = redmine.get_tracker_fields("hoge-project", "4")
    end_time = time.time()
    
    if fields_result['success']:
        print(f"[SUCCESS] Retrieved fields in {end_time - start_time:.2f} seconds")
        print(f"Total fields: {len(fields_result['fields'])}")
        print(f"Required fields: {len(fields_result['required_fields'])}")
        print(f"Custom fields: {len(fields_result['custom_fields'])}")
        
        # Check for custom field 3 (指摘者)
        custom_field_3 = next((f for f in fields_result['fields'] if f['id'] == 'issue_custom_field_values_3'), None)
        if custom_field_3:
            print(f"[SUCCESS] Custom field 3 found: {custom_field_3['name']}")
        else:
            print("[ERROR] Custom field 3 not found")
            
        # Show some key fields
        key_fields = ['issue_subject', 'issue_status_id', 'issue_priority_id', 'issue_assigned_to_id', 'issue_custom_field_values_3']
        print("\nKey fields:")
        for field_id in key_fields:
            field = next((f for f in fields_result['fields'] if f['id'] == field_id), None)
            if field:
                print(f"  {field_id}: {field['name']} (required: {field['required']})")
            else:
                print(f"  {field_id}: NOT FOUND")
                
    else:
        print(f"[ERROR] Failed to get fields: {fields_result['message']}")
    
    # Compare with default tracker
    print("\nTesting get_tracker_fields without tracker_id (default)...")
    
    start_time = time.time()
    default_fields_result = redmine.get_tracker_fields("hoge-project")
    end_time = time.time()
    
    if default_fields_result['success']:
        print(f"[SUCCESS] Retrieved default fields in {end_time - start_time:.2f} seconds")
        print(f"Total fields: {len(default_fields_result['fields'])}")
        
        # Check if custom field 3 exists in default
        custom_field_3_default = next((f for f in default_fields_result['fields'] if f['id'] == 'issue_custom_field_values_3'), None)
        if custom_field_3_default:
            print("[INFO] Custom field 3 found in default tracker")
        else:
            print("[INFO] Custom field 3 NOT found in default tracker")
    else:
        print(f"[ERROR] Failed to get default fields: {default_fields_result['message']}")
    
    # Logout
    redmine.logout()
    print("Logged out.")

if __name__ == "__main__":
    main()