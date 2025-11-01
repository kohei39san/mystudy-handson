#!/usr/bin/env python3
"""
Test script for get_project_members functionality
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_project_members():
    """Test get_project_members functionality"""
    
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    
    print(f"Using credentials: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("=== ログイン ===")
        login_result = scraper.login(username, password)
        print(f"Login result: {login_result}")
        
        if not login_result.get('success'):
            print("Login failed, cannot proceed with test")
            return
        
        # Get projects first
        print("\n=== プロジェクト取得 ===")
        projects_result = scraper.get_projects()
        if not projects_result.get('success') or not projects_result.get('projects'):
            print("No projects available for testing")
            return
        
        # Test with multiple projects
        for project in projects_result['projects'][:2]:  # Test first 2 projects
            project_id = project['id']
            project_name = project['name']
            
            print(f"\n=== プロジェクト '{project_name}' (ID: {project_id}) のメンバー取得 ===")
            members_result = scraper.get_project_members(project_id)
            print(f"Members result: {members_result}")
            
            if members_result.get('success'):
                members = members_result.get('members', [])
                print(f"Found {len(members)} members:")
                
                for i, member in enumerate(members, 1):
                    print(f"  {i}. {member.get('name', 'Unknown')}")
                    if member.get('id'):
                        print(f"     User ID: {member['id']}")
                    if member.get('roles'):
                        print(f"     Roles: {', '.join(member['roles'])}")
                    if member.get('additional_info'):
                        print(f"     Additional Info: {member['additional_info']}")
                    print()
            else:
                print(f"Failed to get members: {members_result.get('message')}")
        
        # Test with invalid project
        print("\n=== 無効なプロジェクトIDのテスト ===")
        invalid_result = scraper.get_project_members("nonexistent-project")
        print(f"Invalid project result: {invalid_result}")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Logout
        print("\n=== ログアウト ===")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    test_project_members()