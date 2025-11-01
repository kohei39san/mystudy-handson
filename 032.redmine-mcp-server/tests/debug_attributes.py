#!/usr/bin/env python3
"""
Debug script to check attributes table structure
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def debug_attributes():
    """Debug attributes table structure"""
    
    # Get credentials from environment
    username = os.getenv('REDMINE_USERNAME')
    password = os.getenv('REDMINE_PASSWORD')
    
    if not username or not password:
        print("Error: REDMINE_USERNAME and REDMINE_PASSWORD must be set in .env file")
        return
    
    print(f"Using credentials: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("=== ログイン ===")
        login_result = scraper.login(username, password)
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return
        
        # Navigate to issue #118
        issue_id = "118"
        print(f"\n=== チケット#{issue_id}のHTML構造確認 ===")
        
        from config import config
        issue_url = f"{config.base_url}/issues/{issue_id}"
        scraper.driver.get(issue_url)
        
        import time
        time.sleep(2)
        
        from selenium.webdriver.common.by import By
        
        # Check various selectors for attributes
        selectors_to_test = [
            "#content > div.issue.details > div.attributes tr",
            ".issue.details .attributes tr",
            ".attributes tr",
            "div.attributes tr",
            ".issue.details tr",
            "#content tr"
        ]
        
        print("Testing attribute selectors:")
        for selector in selectors_to_test:
            try:
                elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  {selector}: {len(elements)} elements found")
                
                if elements:
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        cells = elem.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            field_name = cells[0].text.strip()
                            field_value = cells[1].text.strip()
                            print(f"    [{i}] {field_name}: {field_value}")
                        else:
                            print(f"    [{i}] {len(cells)} cells: {elem.text.strip()}")
                            
            except Exception as e:
                print(f"  {selector}: Error - {e}")
        
        # Check for div.attribute elements (individual field containers)
        print("\nTesting individual attribute divs:")
        attribute_divs = scraper.driver.find_elements(By.CSS_SELECTOR, "div.attribute")
        print(f"Found {len(attribute_divs)} div.attribute elements")
        
        for i, div in enumerate(attribute_divs[:10]):  # Show first 10
            try:
                # Get class names to identify field type
                class_names = div.get_attribute("class")
                
                # Try to get label and value
                label_elem = div.find_element(By.CSS_SELECTOR, "div.label")
                value_elem = div.find_element(By.CSS_SELECTOR, "div.value")
                
                label_text = label_elem.text.strip()
                value_text = value_elem.text.strip()
                
                print(f"  [{i}] {class_names}: {label_text} = {value_text}")
                
            except Exception as e:
                print(f"  [{i}] Error processing div: {e}")
        
    finally:
        # Logout
        print("\n=== ログアウト ===")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    debug_attributes()