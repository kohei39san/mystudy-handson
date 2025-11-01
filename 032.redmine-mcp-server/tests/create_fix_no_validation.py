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
    
    # Create ticket with 修正 tracker - bypassing validation
    print("Creating ticket with 修正 tracker (no validation)...")
    
    # Manually navigate and set fields without using create_issue validation
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select
    import time
    
    # Navigate to new issue page
    new_issue_url = "http://168.138.42.184/projects/hoge-project/issues/new"
    redmine.driver.get(new_issue_url)
    time.sleep(3)
    
    # Set tracker first
    tracker_element = redmine.driver.find_element(By.ID, "issue_tracker_id")
    select = Select(tracker_element)
    select.select_by_value("4")
    time.sleep(3)  # Wait for tracker-specific fields to load
    
    # Set subject
    subject_element = redmine.driver.find_element(By.ID, "issue_subject")
    subject_element.clear()
    subject_element.send_keys("修正トラッカーテストチケット - 指摘者・担当者・親チケット指定")
    
    # Set description
    desc_element = redmine.driver.find_element(By.ID, "issue_description")
    desc_element.clear()
    desc_element.send_keys("このチケットは修正トラッカーで作成され、指摘者、担当者、親チケットが指定されています。")
    
    # Set status
    status_element = redmine.driver.find_element(By.ID, "issue_status_id")
    status_select = Select(status_element)
    status_select.select_by_value("1")
    
    # Set priority
    priority_element = redmine.driver.find_element(By.ID, "issue_priority_id")
    priority_select = Select(priority_element)
    priority_select.select_by_value("2")
    
    # Set assignee
    assignee_element = redmine.driver.find_element(By.ID, "issue_assigned_to_id")
    assignee_select = Select(assignee_element)
    assignee_select.select_by_value("1")
    
    # Set parent issue
    parent_element = redmine.driver.find_element(By.ID, "issue_parent_issue_id")
    parent_element.clear()
    parent_element.send_keys("134")
    
    # Set custom field (reporter)
    custom_element = redmine.driver.find_element(By.ID, "issue_custom_field_values_3")
    custom_select = Select(custom_element)
    custom_select.select_by_value("1")
    
    print("All fields set, submitting form...")
    
    # Submit form
    submit_button = redmine.driver.find_element(By.CSS_SELECTOR, "input[name=commit]")
    submit_button.click()
    
    # Wait for redirect
    time.sleep(5)
    
    # Check result
    current_url = redmine.driver.current_url
    print(f"URL after submit: {current_url}")
    print(f"Page title: {redmine.driver.title}")
    
    if '/issues/' in current_url and 'new' not in current_url:
        # Extract issue ID
        import re
        issue_id_match = re.search(r'/issues/(\d+)', current_url)
        if issue_id_match:
            issue_id = issue_id_match.group(1)
            print(f"[SUCCESS] Created issue #{issue_id}")
            print(f"Issue URL: {current_url}")
            
            # Get issue details
            details = redmine.get_issue_details(issue_id)
            if details['success']:
                print("\\nTicket details:")
                for field, value in details['issue'].items():
                    print(f"  {field}: {value}")
        else:
            print("[ERROR] Could not extract issue ID from URL")
    else:
        print(f"[ERROR] Unexpected redirect to: {current_url}")
    
    # Logout
    redmine.logout()
    print("Logged out.")

if __name__ == "__main__":
    main()