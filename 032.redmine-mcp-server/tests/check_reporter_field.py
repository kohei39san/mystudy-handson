#!/usr/bin/env python3
"""
Check if reporter field (指摘者) is available in tracker fields
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def check_reporter_field():
    """Check if reporter field is available"""
    
    # Get credentials from environment
    username = os.getenv('REDMINE_USERNAME')
    password = os.getenv('REDMINE_PASSWORD')
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        login_result = scraper.login(username, password)
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return
        
        # Get tracker fields for 修正 tracker (ID: 4)
        project_id = 'hoge-project'
        tracker_id = '4'
        
        print(f"=== Getting tracker fields for project {project_id}, tracker {tracker_id} ===")
        fields_result = scraper.get_tracker_fields(project_id, tracker_id)
        
        if fields_result['success']:
            print(f"Total fields: {len(fields_result['fields'])}")
            
            # Look for reporter field (指摘者)
            reporter_fields = []
            parent_fields = []
            
            for field in fields_result['fields']:
                field_id = field['id']
                field_name = field['name']
                
                # Check for reporter field
                if ('指摘者' in field_name or 'reporter' in field_name.lower() or 
                    field_id == 'issue_custom_field_values_3'):
                    reporter_fields.append(field)
                
                # Check for parent field
                if ('parent' in field_name.lower() or '親' in field_name or 
                    field_id == 'issue_parent_issue_id'):
                    parent_fields.append(field)
            
            print(f"\n=== Reporter fields found: {len(reporter_fields)} ===")
            for field in reporter_fields:
                print(f"  ID: {field['id']}")
                print(f"  Name: {field['name']}")
                print(f"  Type: {field['type']}")
                print(f"  Required: {field['required']}")
                print(f"  Custom: {field.get('custom', False)}")
                print()
            
            print(f"=== Parent fields found: {len(parent_fields)} ===")
            for field in parent_fields:
                print(f"  ID: {field['id']}")
                print(f"  Name: {field['name']}")
                print(f"  Type: {field['type']}")
                print(f"  Required: {field['required']}")
                print(f"  Custom: {field.get('custom', False)}")
                print()
            
            # Show all custom fields
            custom_fields = [f for f in fields_result['fields'] if f.get('custom', False)]
            print(f"=== All custom fields: {len(custom_fields)} ===")
            for field in custom_fields:
                print(f"  {field['id']}: {field['name']} ({field['type']})")
            
        else:
            print(f"Failed to get tracker fields: {fields_result['message']}")
        
    finally:
        scraper.logout()

if __name__ == "__main__":
    check_reporter_field()