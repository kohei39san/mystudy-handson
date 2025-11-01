#!/usr/bin/env python3
"""
Debug script to check subject selectors
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from redmine_selenium import RedmineSeleniumScraper

def debug_subject_selectors():
    """Debug subject selectors for issue #118"""
    
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
        
        # Try various selectors
        selectors_to_test = [
            "#content > div.issue.details > div:nth-child(3) > div.subject > div > h3",
            "#sticky-issue-header > span.issue-heading",
            "h3",
            ".subject h3",
            ".issue.details .subject h3",
            "#content .subject h3",
            "div.subject h3",
            ".subject",
            "h1",
            "h2",
            ".issue-heading"
        ]
        
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        
        print("Testing selectors:")
        for selector in selectors_to_test:
            try:
                elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for i, elem in enumerate(elements):
                        text = elem.text.strip()
                        if text:
                            print(f"  OK {selector} [{i}]: '{text}'")
                        else:
                            print(f"  OK {selector} [{i}]: (empty)")
                else:
                    print(f"  NG {selector}: No elements found")
            except Exception as e:
                print(f"  NG {selector}: Error - {e}")
        
        # Get page source snippet around subject area
        print("\n=== HTML構造の確認 ===")
        try:
            # Look for elements containing "Test Subject for Issue Creation"
            page_source = scraper.driver.page_source
            if "Test Subject for Issue Creation" in page_source:
                print("OK Subject text found in page source")
                
                # Find the context around the subject
                import re
                pattern = r'.{0,200}Test Subject for Issue Creation.{0,200}'
                matches = re.findall(pattern, page_source, re.DOTALL)
                for i, match in enumerate(matches):
                    print(f"Context {i+1}: {match}")
            else:
                print("NG Subject text not found in page source")
                
                # Show first 2000 characters of page source
                print("Page source snippet:")
                print(page_source[:2000])
                
        except Exception as e:
            print(f"Error checking page source: {e}")
        
    finally:
        # Logout
        print("\n=== ログアウト ===")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    debug_subject_selectors()