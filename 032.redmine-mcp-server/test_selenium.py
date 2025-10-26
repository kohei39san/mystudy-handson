#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Redmine Selenium Scraper
"""

import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from redmine_selenium import RedmineSeleniumScraper
from config import config

async def test_selenium_scraper():
    """Test the Redmine Selenium scraper functionality"""
    print("[SELENIUM] Testing Redmine Selenium Scraper")
    print(f"Target URL: {config.base_url}")
    print("=" * 50)
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Test server info
        print("\n[INFO] Server Configuration:")
        print(f"  Base URL: {config.base_url}")
        print(f"  Login URL: {config.login_url}")
        print(f"  Projects URL: {config.projects_url}")
        
        # Get credentials from environment variables
        print("\n[AUTH] Authentication Test:")
        username = os.getenv('REDMINE_USERNAME')
        password = os.getenv('REDMINE_PASSWORD')
        
        if username and password:
            print(f"Using credentials from environment for user: {username}")
            
            print("\n[LOGIN] Attempting login with Selenium...")
            login_result = scraper.login(username, password)
            
            print(f"Login Result: {json.dumps(login_result, indent=2)}")
            
            if login_result.get('success'):
                print("\n[PROJECTS] Fetching projects...")
                projects_result = scraper.get_projects()
                
                print(f"Projects Result: {json.dumps(projects_result, indent=2)}")
                
                # Display project details
                projects = projects_result.get('projects', [])
                if projects:
                    print(f"\n[SUCCESS] Found {len(projects)} project(s):")
                    for i, project in enumerate(projects, 1):
                        print(f"  {i}. Name: {project.get('name', 'N/A')}")
                        print(f"     ID: {project.get('id', 'N/A')}")
                        print(f"     URL: {project.get('url', 'N/A')}")
                        print(f"     Description: {project.get('description', 'N/A')}")
                        print()
                else:
                    print("\n[INFO] No projects found")
                
                print("\n[LOGOUT] Logging out...")
                logout_result = scraper.logout()
                print(f"Logout Result: {json.dumps(logout_result, indent=2)}")
            else:
                print("[ERROR] Login failed, skipping project fetch test")
        else:
            print("[SKIP] No credentials found in environment variables (REDMINE_USERNAME, REDMINE_PASSWORD)")
        
        print("\n[DONE] Selenium test completed!")
        
    except Exception as e:
        print(f"\n[ERROR] Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure cleanup
        try:
            scraper.logout()
        except:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(test_selenium_scraper())
    except KeyboardInterrupt:
        print("\n[STOP] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)