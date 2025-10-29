#!/usr/bin/env python3
"""
Test script for text search functionality in search_issues
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

# Set up logging to see debug output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_text_search():
    """Test text search functionality"""
    
    # Get credentials from environment with defaults
    username = os.getenv('REDMINE_USERNAME', 'admin')
    password = os.getenv('REDMINE_PASSWORD', 'admin')
    
    print(f"Using credentials: {username}/{password}")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login(username, password)
        print(f"Login result: {login_result}")
        
        if not login_result.get('success'):
            print("Login failed, cannot proceed with test")
            return
        
        # Test 1: Search with 'q' parameter (general text search)
        print("\n=== Test 1: General text search with 'q' parameter ===")
        search_result = scraper.search_issues(q="TEST")
        print(f"Search result for q='TEST': {search_result['success']}")
        print(f"Number of issues found: {len(search_result.get('issues', []))}")
        print(f"Total count: {search_result.get('total_count', 0)}")
        
        # Test 2: Search with 'subject' parameter
        print("\n=== Test 2: Subject text search ===")
        search_result = scraper.search_issues(subject="チケット")
        print(f"Search result for subject='チケット': {search_result['success']}")
        print(f"Number of issues found: {len(search_result.get('issues', []))}")
        print(f"Total count: {search_result.get('total_count', 0)}")
        
        # Test 3: Search with 'description' parameter
        print("\n=== Test 3: Description text search ===")
        search_result = scraper.search_issues(description="説明")
        print(f"Search result for description='説明': {search_result['success']}")
        print(f"Number of issues found: {len(search_result.get('issues', []))}")
        print(f"Total count: {search_result.get('total_count', 0)}")
        
        # Test 4: Search with 'notes' parameter
        print("\n=== Test 4: Notes text search ===")
        search_result = scraper.search_issues(notes="コメント")
        print(f"Search result for notes='コメント': {search_result['success']}")
        print(f"Number of issues found: {len(search_result.get('issues', []))}")
        print(f"Total count: {search_result.get('total_count', 0)}")
        
        # Test 5: Search with non-existent text
        print("\n=== Test 5: Non-existent text search ===")
        search_result = scraper.search_issues(q="NONEXISTENT_TEXT_12345")
        print(f"Search result for q='NONEXISTENT_TEXT_12345': {search_result['success']}")
        print(f"Number of issues found: {len(search_result.get('issues', []))}")
        print(f"Total count: {search_result.get('total_count', 0)}")
        
        # Test 6: Combined search (tracker_id + text)
        print("\n=== Test 6: Combined search (tracker_id + text) ===")
        search_result = scraper.search_issues(tracker_id=1, q="TEST")
        print(f"Search result for tracker_id=1 + q='TEST': {search_result['success']}")
        print(f"Number of issues found: {len(search_result.get('issues', []))}")
        print(f"Total count: {search_result.get('total_count', 0)}")
        
        # Test 7: Show some sample results
        print("\n=== Test 7: Sample results from general search ===")
        search_result = scraper.search_issues(q="TEST")
        if search_result.get('success') and search_result.get('issues'):
            print("Sample issues found:")
            for i, issue in enumerate(search_result['issues'][:3]):  # Show first 3
                print(f"  {i+1}. #{issue.get('id')} - {issue.get('subject', 'No subject')}")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Logout
        print("\nLogging out...")
        logout_result = scraper.logout()
        print(f"Logout result: {logout_result}")

if __name__ == "__main__":
    test_text_search()