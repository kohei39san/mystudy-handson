#!/usr/bin/env python3
"""
Debug script to check what fields are available for 修正 tracker
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def debug_tracker_fields():
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("admin", "admin")
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return
        
        # Get tracker fields for 修正 tracker
        print("Getting tracker fields for 修正 tracker (ID: 4)...")
        fields_result = scraper.get_tracker_fields("hoge-project", "4")
        
        if fields_result['success']:
            fields = fields_result['fields']
            print(f"Total fields: {len(fields)}")
            
            print("\nRequired fields:")
            for field in fields:
                if field.get('required'):
                    print(f"  - {field['name']} (ID: {field['id']})")
                    if field.get('options'):
                        print(f"    Options: {field['options'][:3]}...")  # Show first 3 options
            
            print("\nAll fields:")
            for field in fields:
                req_str = " [REQUIRED]" if field.get('required') else ""
                print(f"  - {field['name']} (ID: {field['id']}){req_str}")
        else:
            print(f"Failed to get fields: {fields_result['message']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            scraper.logout()
            scraper.close()
        except:
            pass

if __name__ == "__main__":
    debug_tracker_fields()