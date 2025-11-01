#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
import config

def test_tracker_fields():
    scraper = RedmineSeleniumScraper()
    
    # Login
    import os
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    login_result = scraper.login(username, password)
    if not login_result['success']:
        print(f"Login failed: {login_result['message']}")
        return
    
    print("Login successful")
    
    # Get tracker fields for 修正 tracker (ID: 4)
    result = scraper.get_tracker_fields('hoge-project', '4')
    
    if result['success']:
        print(f"\n修正トラッカーのフィールド一覧:")
        print(f"Total fields: {len(result['fields'])}")
        
        for field in result['fields']:
            print(f"ID: {field['id']}")
            print(f"  Name: {field['name']}")
            print(f"  Type: {field['type']}")
            print(f"  Required: {field['required']}")
            print(f"  Visible: {field['visible']}")
            print(f"  Enabled: {field['enabled']}")
            if 'options' in field:
                print(f"  Options: {len(field['options'])} items")
            print()
    else:
        print(f"Failed to get tracker fields: {result['message']}")
    
    scraper.logout()

if __name__ == "__main__":
    test_tracker_fields()