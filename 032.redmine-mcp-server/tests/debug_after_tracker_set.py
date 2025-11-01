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
    
    # Navigate to new issue page
    print("Navigating to new issue page...")
    new_issue_url = "http://168.138.42.184/projects/hoge-project/issues/new"
    redmine.driver.get(new_issue_url)
    time.sleep(3)
    
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select
    
    print(f"Current URL: {redmine.driver.current_url}")
    
    # Set tracker to 4 (修正) - same as in create_issue method
    print("Setting tracker to 4...")
    tracker_element = redmine.driver.find_element(By.CSS_SELECTOR, "#issue_tracker_id")
    select = Select(tracker_element)
    select.select_by_value("4")
    print("Tracker set, waiting 3 seconds...")
    time.sleep(3)
    
    print(f"URL after tracker set: {redmine.driver.current_url}")
    
    # Check if the expected fields exist
    expected_fields = [
        "issue_subject",
        "issue_description", 
        "issue_status_id",
        "issue_priority_id",
        "issue_assigned_to_id",
        "issue_parent_issue_id",
        "issue_custom_field_values_3"
    ]
    
    print("\\nChecking for expected fields:")
    for field_id in expected_fields:
        elements = redmine.driver.find_elements(By.ID, field_id)
        if elements:
            element = elements[0]
            print(f"  [OK] {field_id}: Found ({element.tag_name}, visible: {element.is_displayed()}, enabled: {element.is_enabled()})")
        else:
            print(f"  [MISSING] {field_id}: NOT FOUND")
    
    # Check if we're still on the new issue page
    if 'new' not in redmine.driver.current_url:
        print(f"\\nWARNING: Not on new issue page anymore!")
        print(f"Current page title: {redmine.driver.title}")
        print(f"Page source snippet: {redmine.driver.page_source[:500]}")
    
    # Logout
    redmine.logout()
    print("Logged out.")

if __name__ == "__main__":
    main()