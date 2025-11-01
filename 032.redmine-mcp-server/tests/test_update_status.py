#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for updating issue status
"""

import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
from config import config

async def test_update_status():
    """Test updating issue status to 対応中 (In Progress)"""
    print("[UPDATE STATUS] Testing Issue Status Update")
    print(f"Target URL: {config.base_url}")
    print("=" * 50)
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Authentication via browser
        print("\n[AUTH] Please login via browser when prompted")
        
        print(f"\n[LOGIN] Attempting login with Selenium (browser authentication)")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print(f"Login successful!")
            
            # Get current issue details
            issue_id = "101"
            print(f"\n[DETAILS] Getting current details for issue #{issue_id}")
            details_result = scraper.get_issue_details(issue_id)
            
            if details_result.get('success'):
                current_issue = details_result['issue']
                print(f"Current status: {current_issue.get('status', 'Unknown')}")
                print(f"Current subject: {current_issue.get('subject', 'Unknown')}")
                
                # Try different status IDs for "対応中" (In Progress)
                # Common status IDs: 1=New, 2=In Progress, 3=Resolved, 5=Closed
                status_candidates = ["2", "進行中", "対応中", "In Progress"]
                
                for status_id in status_candidates:
                    print(f"\n[UPDATE] Trying to update status to: {status_id}")
                    update_result = scraper.update_issue(
                        issue_id, 
                        status_id=status_id,
                        notes=f"Status changed to {status_id} (test)"
                    )
                    
                    print(f"Update result: {json.dumps(update_result, indent=2)}")
                    
                    if update_result.get('success'):
                        print(f"[SUCCESS] Successfully updated status to: {status_id}")
                        
                        # Verify the change
                        print(f"\n[VERIFY] Verifying the status change...")
                        verify_result = scraper.get_issue_details(issue_id)
                        if verify_result.get('success'):
                            new_status = verify_result['issue'].get('status', 'Unknown')
                            print(f"New status: {new_status}")
                        break
                    else:
                        print(f"[FAILED] Failed to update with status_id: {status_id}")
                        print(f"Error: {update_result.get('message', 'Unknown error')}")
            else:
                print(f"Failed to get issue details: {details_result.get('message')}")
            
            print("\n[LOGOUT] Logging out...")
            logout_result = scraper.logout()
            print(f"Logout: {logout_result.get('message')}")
        else:
            print("[ERROR] Login failed")
        
        print("\n[DONE] Status update test completed!")
        
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
        asyncio.run(test_update_status())
    except KeyboardInterrupt:
        print("\n[STOP] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)