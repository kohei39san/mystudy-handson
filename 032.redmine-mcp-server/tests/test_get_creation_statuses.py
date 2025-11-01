#!/usr/bin/env python3
"""
Test script for get_creation_statuses method
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_get_creation_statuses():
    """Test get_creation_statuses method for different trackers"""
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in to Redmine...")
        login_result = scraper.login("admin", "admin")
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return False
        print("[OK] Login successful")
        
        project_id = "hoge-project"
        trackers = [
            {"id": "1", "name": "課題"},
            {"id": "2", "name": "タスク"},
            {"id": "4", "name": "修正"}
        ]
        
        print(f"Testing creation statuses for project: {project_id}")
        print("=" * 60)
        
        for tracker in trackers:
            print(f"Tracker: {tracker['name']} (ID: {tracker['id']})")
            
            statuses_result = scraper.get_creation_statuses(project_id, tracker['id'])
            
            if statuses_result['success']:
                statuses = statuses_result['statuses']
                print(f"  [OK] {statuses_result['message']}")
                print(f"  Available statuses:")
                
                for i, status in enumerate(statuses, 1):
                    print(f"    {i}. {status['text']} (ID: {status['value']})")
                
                print()
            else:
                print(f"  [ERROR] {statuses_result['message']}")
                print()
        
        return True
            
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
    print("=== Test: get_creation_statuses for different trackers ===")
    success = test_get_creation_statuses()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)