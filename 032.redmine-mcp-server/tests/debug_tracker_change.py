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
    
    print(f"Current URL: {redmine.driver.current_url}")
    print(f"Page title: {redmine.driver.title}")
    
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select
    
    # Check initial tracker
    tracker_select = redmine.driver.find_element(By.ID, "issue_tracker_id")
    select = Select(tracker_select)
    current_tracker = select.first_selected_option.get_attribute('value')
    print(f"Initial tracker: {current_tracker}")
    
    # Look for custom field 3 before changing tracker
    custom_field_3_before = redmine.driver.find_elements(By.ID, "issue_custom_field_values_3")
    print(f"Custom field 3 before tracker change: {len(custom_field_3_before)} found")
    
    # Change to tracker 4 (修正)
    print("Changing to tracker 4 (修正)...")
    select.select_by_value("4")
    time.sleep(3)  # Wait for any AJAX updates
    
    # Check if URL changed or page reloaded
    print(f"URL after tracker change: {redmine.driver.current_url}")
    
    # Look for custom field 3 after changing tracker
    custom_field_3_after = redmine.driver.find_elements(By.ID, "issue_custom_field_values_3")
    print(f"Custom field 3 after tracker change: {len(custom_field_3_after)} found")
    
    if custom_field_3_after:
        field = custom_field_3_after[0]
        print(f"Custom field 3 details:")
        print(f"  Tag: {field.tag_name}")
        print(f"  Type: {field.get_attribute('type')}")
        print(f"  Name: {field.get_attribute('name')}")
        print(f"  ID: {field.get_attribute('id')}")
        print(f"  Visible: {field.is_displayed()}")
        print(f"  Enabled: {field.is_enabled()}")
    
    # Look for all form elements again
    print("\n=== FORM ELEMENTS AFTER TRACKER CHANGE ===")
    elements = redmine.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
    
    relevant_elements = []
    for element in elements:
        elem_id = element.get_attribute('id')
        elem_name = element.get_attribute('name')
        if elem_id and ('issue_' in elem_id or 'custom_field' in elem_id):
            relevant_elements.append(element)
    
    print(f"Found {len(relevant_elements)} relevant form elements:")
    for element in relevant_elements:
        tag = element.tag_name
        elem_type = element.get_attribute('type') or tag
        elem_id = element.get_attribute('id')
        elem_name = element.get_attribute('name')
        print(f"  {tag}[{elem_type}] id='{elem_id}' name='{elem_name}'")
    
    # Logout
    redmine.logout()
    print("Logged out.")

if __name__ == "__main__":
    main()