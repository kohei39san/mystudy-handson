#!/usr/bin/env python3
"""
Test script for get_available_trackers with fields
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_get_available_trackers_with_fields():
    """Test get_available_trackers method with fields included"""
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in to Redmine...")
        login_result = scraper.login("admin", "admin")
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return False
        print("[OK] Login successful")
        
        # Test get_available_trackers with project_id
        project_id = "hoge-project"
        print(f"Getting available trackers with fields for: {project_id}")
        
        trackers_result = scraper.get_available_trackers(project_id)
        
        if trackers_result['success']:
            trackers = trackers_result['trackers']
            print(f"[OK] {trackers_result['message']}")
            print("=" * 60)
            
            for i, tracker in enumerate(trackers, 1):
                print(f"{i}. {tracker['text']} (ID: {tracker['value']})")
                
                if 'fields' in tracker:
                    fields = tracker['fields']
                    required_fields = tracker.get('required_fields', [])
                    optional_fields = tracker.get('optional_fields', [])
                    
                    print(f"   Total fields: {len(fields)}")
                    print(f"   Required: {len(required_fields)}")
                    print(f"   Optional: {len(optional_fields)}")
                    
                    if required_fields:
                        print("   Required fields:")
                        for field in required_fields[:3]:  # Show first 3
                            print(f"     - {field['name']} ({field['id']})")
                        if len(required_fields) > 3:
                            print(f"     ... and {len(required_fields) - 3} more")
                else:
                    print("   Fields: Not available")
                
                print()
            
            return True
        else:
            print(f"[ERROR] {trackers_result['message']}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False
    finally:
        try:
            scraper.logout()
            scraper.close()
        except:
            pass

if __name__ == "__main__":
    print("=== Test: get_available_trackers with fields ===")
    success = test_get_available_trackers_with_fields()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)