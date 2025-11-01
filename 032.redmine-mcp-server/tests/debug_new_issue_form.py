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
    
    # Check if we're on the right page
    if 'new' not in redmine.driver.current_url.lower():
        print("ERROR: Not on new issue page!")
        print(f"Page source snippet: {redmine.driver.page_source[:500]}")
        return
    
    # Look for all input, select, and textarea elements
    from selenium.webdriver.common.by import By
    
    print("\n=== FORM ELEMENTS ===")
    elements = redmine.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
    
    for i, element in enumerate(elements):
        tag = element.tag_name
        elem_type = element.get_attribute('type') or tag
        elem_id = element.get_attribute('id')
        elem_name = element.get_attribute('name')
        elem_value = element.get_attribute('value')
        
        if elem_id or elem_name:
            print(f"  {i+1}. {tag}[{elem_type}] id='{elem_id}' name='{elem_name}' value='{elem_value}'")
    
    print("\n=== LOOKING FOR SPECIFIC FIELDS ===")
    
    # Look for tracker field
    tracker_fields = redmine.driver.find_elements(By.CSS_SELECTOR, "select[name*='tracker'], select[id*='tracker']")
    print(f"Tracker fields found: {len(tracker_fields)}")
    for field in tracker_fields:
        print(f"  ID: {field.get_attribute('id')}, Name: {field.get_attribute('name')}")
    
    # Look for subject field
    subject_fields = redmine.driver.find_elements(By.CSS_SELECTOR, "input[name*='subject'], input[id*='subject']")
    print(f"Subject fields found: {len(subject_fields)}")
    for field in subject_fields:
        print(f"  ID: {field.get_attribute('id')}, Name: {field.get_attribute('name')}")
    
    # Look for description field
    desc_fields = redmine.driver.find_elements(By.CSS_SELECTOR, "textarea[name*='description'], textarea[id*='description']")
    print(f"Description fields found: {len(desc_fields)}")
    for field in desc_fields:
        print(f"  ID: {field.get_attribute('id')}, Name: {field.get_attribute('name')}")
    
    # Look for status field
    status_fields = redmine.driver.find_elements(By.CSS_SELECTOR, "select[name*='status'], select[id*='status']")
    print(f"Status fields found: {len(status_fields)}")
    for field in status_fields:
        print(f"  ID: {field.get_attribute('id')}, Name: {field.get_attribute('name')}")
    
    # Look for priority field
    priority_fields = redmine.driver.find_elements(By.CSS_SELECTOR, "select[name*='priority'], select[id*='priority']")
    print(f"Priority fields found: {len(priority_fields)}")
    for field in priority_fields:
        print(f"  ID: {field.get_attribute('id')}, Name: {field.get_attribute('name')}")
    
    # Logout
    redmine.logout()
    print("Logged out.")

if __name__ == "__main__":
    main()