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
    time.sleep(2)
    
    # Set tracker to 修正 (ID: 4)
    print("Setting tracker to 修正...")
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.common.by import By
    
    tracker_select = redmine.driver.find_element(By.ID, "issue_tracker_id")
    select = Select(tracker_select)
    select.select_by_value("4")
    time.sleep(2)
    
    # Look for all submit buttons
    print("Looking for submit buttons...")
    submit_buttons = redmine.driver.find_elements(By.CSS_SELECTOR, "input[type=submit], button[type=submit]")
    
    print(f"Found {len(submit_buttons)} submit buttons:")
    for i, button in enumerate(submit_buttons):
        print(f"  Button {i+1}:")
        print(f"    Tag: {button.tag_name}")
        print(f"    Type: {button.get_attribute('type')}")
        print(f"    Name: {button.get_attribute('name')}")
        print(f"    ID: {button.get_attribute('id')}")
        print(f"    Value: {button.get_attribute('value')}")
        print(f"    Text: {button.text}")
        print(f"    Class: {button.get_attribute('class')}")
        
        # Get parent form info
        try:
            parent_form = button.find_element(By.XPATH, "ancestor::form[1]")
            print(f"    Parent form ID: {parent_form.get_attribute('id')}")
            print(f"    Parent form class: {parent_form.get_attribute('class')}")
        except:
            print(f"    No parent form found")
        print()
    
    # Look for forms
    print("Looking for forms...")
    forms = redmine.driver.find_elements(By.TAG_NAME, "form")
    print(f"Found {len(forms)} forms:")
    for i, form in enumerate(forms):
        print(f"  Form {i+1}:")
        print(f"    ID: {form.get_attribute('id')}")
        print(f"    Class: {form.get_attribute('class')}")
        print(f"    Action: {form.get_attribute('action')}")
        print()
    
    # Logout
    redmine.logout()
    print("Logged out.")

if __name__ == "__main__":
    main()