#!/usr/bin/env python3
"""
Test script for get_project_members method with current user detection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

def test_get_project_members():
    """Test get_project_members method with current user detection"""
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in to Redmine...")
        login_result = scraper.login("admin", "admin")
        if not login_result['success']:
            print(f"Login failed: {login_result['message']}")
            return False
        print("[OK] Login successful")
        
        # Test get_project_members
        project_id = "hoge-project"
        print(f"Getting project members for: {project_id}")
        
        members_result = scraper.get_project_members(project_id)
        
        if members_result['success']:
            members = members_result['members']
            print(f"[OK] {members_result['message']}")
            print(f"Found {len(members)} members:")
            print("=" * 50)
            
            current_user_found = False
            for i, member in enumerate(members, 1):
                print(f"{i}. {member['name']} (ID: {member['id']})")
                print(f"   Current User: {'YES' if member.get('is_current_user') else 'NO'}")
                if member.get('roles'):
                    print(f"   Roles: {', '.join(member['roles'])}")
                if member.get('additional_info'):
                    print(f"   Additional Info: {member['additional_info']}")
                print()
                
                if member.get('is_current_user'):
                    current_user_found = True
            
            print("=" * 50)
            print(f"Current user detected: {'YES' if current_user_found else 'NO'}")
            
            return True
        else:
            print(f"[ERROR] {members_result['message']}")
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
    print("=== Test: get_project_members with current user detection ===")
    success = test_get_project_members()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)