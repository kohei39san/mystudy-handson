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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from redmine_selenium import RedmineSeleniumScraper
from config import config

async def check_issue_details():
    """Check issue details to see tracker information"""
    print("=== Issue Details Check ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Check details of issue #101
            issue_id = "101"
            print(f"\n--- Getting details for issue #{issue_id} ---")
            details_result = scraper.get_issue_details(issue_id)
            
            if details_result.get('success'):
                issue = details_result['issue']
                print("Issue details:")
                for key, value in issue.items():
                    print(f"  {key}: {value}")
                
                # Check if tracker is available
                if 'tracker' in issue:
                    tracker_name = issue['tracker']
                    print(f"\nFound tracker: '{tracker_name}'")
                    
                    # Test search with this tracker
                    print(f"Testing search with tracker '{tracker_name}'...")
                    search_result = scraper.search_issues(tracker_id=tracker_name, per_page=5)
                    
                    if search_result.get('success'):
                        found_count = search_result.get('total_count', 0)
                        print(f"Search result: {found_count} issues found with tracker '{tracker_name}'")
                        
                        if search_result.get('issues'):
                            print("Sample results:")
                            for i, issue in enumerate(search_result['issues'][:3], 1):
                                print(f"  {i}. #{issue.get('id')} - {issue.get('subject')}")
                    else:
                        print(f"Search failed: {search_result.get('message')}")
                else:
                    print("No tracker information found in issue details")
            else:
                print(f"Failed to get issue details: {details_result.get('message')}")
            
            # Logout
            scraper.logout()
            print("\n[OK] Logged out")
        else:
            print("[FAIL] Login failed")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.logout()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(check_issue_details())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check what trackers exist in the system
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

async def check_trackers():
    """Check existing trackers in the system"""
    print("=== Tracker Check ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Get all issues to see what trackers exist
            print("\n--- Getting all issues to check trackers ---")
            search_result = scraper.search_issues(per_page=25)
            
            if search_result.get('success'):
                issues = search_result.get('issues', [])
                total_count = search_result.get('total_count', 0)
                print(f"Found {total_count} total issues")
                
                # Collect unique trackers
                trackers = set()
                for issue in issues:
                    if issue.get('tracker'):
                        trackers.add(issue['tracker'])
                
                print(f"\nFound trackers in existing issues:")
                for tracker in sorted(trackers):
                    print(f"  - {tracker}")
                
                # Show some sample issues with their trackers
                print(f"\nSample issues with tracker info:")
                for i, issue in enumerate(issues[:5], 1):
                    print(f"  {i}. #{issue.get('id')} - {issue.get('subject', 'No subject')}")
                    print(f"     Tracker: {issue.get('tracker', 'Unknown')}")
                    print(f"     Status: {issue.get('status', 'Unknown')}")
                    print()
                
                # Test search with actual tracker names found
                if trackers:
                    print("--- Testing search with found tracker names ---")
                    for tracker in sorted(trackers):
                        print(f"\nSearching for tracker: '{tracker}'")
                        tracker_search = scraper.search_issues(tracker_id=tracker, per_page=5)
                        if tracker_search.get('success'):
                            found_count = tracker_search.get('total_count', 0)
                            print(f"  Result: {found_count} issues found")
                        else:
                            print(f"  Error: {tracker_search.get('message')}")
            else:
                print(f"Failed to get issues: {search_result.get('message')}")
            
            # Logout
            scraper.logout()
            print("\n[OK] Logged out")
        else:
            print("[FAIL] Login failed")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.logout()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(check_trackers())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get available trackers from issue edit page
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

async def get_trackers_from_edit():
    """Get available trackers from issue edit page"""
    print("=== Get Trackers from Edit Page ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Navigate to issue edit page to get tracker options
            issue_id = "101"
            edit_url = f"{config.base_url}/issues/{issue_id}/edit"
            print(f"\nNavigating to edit page: {edit_url}")
            
            scraper.driver.get(edit_url)
            
            # Wait for page to load
            import time
            time.sleep(3)
            
            # Get tracker options
            try:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import Select
                
                tracker_select = scraper.driver.find_element(By.ID, "issue_tracker_id")
                select = Select(tracker_select)
                
                print("Available trackers:")
                trackers = []
                for option in select.options:
                    value = option.get_attribute('value')
                    text = option.text.strip()
                    if value:  # Skip empty values
                        trackers.append({
                            'value': value,
                            'text': text
                        })
                        print(f"  - {text} (ID: {value})")
                
                # Test search with each tracker
                if trackers:
                    print(f"\n--- Testing search with each tracker ---")
                    for tracker in trackers:
                        print(f"\nTesting tracker ID '{tracker['value']}' ({tracker['text']}):")
                        
                        # Test with ID
                        search_result = scraper.search_issues(tracker_id=tracker['value'], per_page=5)
                        if search_result.get('success'):
                            count = search_result.get('total_count', 0)
                            print(f"  By ID: {count} issues found")
                        
                        # Test with name
                        search_result = scraper.search_issues(tracker_id=tracker['text'], per_page=5)
                        if search_result.get('success'):
                            count = search_result.get('total_count', 0)
                            print(f"  By name: {count} issues found")
                
            except Exception as e:
                print(f"Error getting tracker options: {e}")
            
            # Logout
            scraper.logout()
            print("\n[OK] Logged out")
        else:
            print("[FAIL] Login failed")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.logout()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(get_trackers_from_edit())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to update issue #101 status to "In Progress" (status_id=2)
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

async def simple_status_update():
    """Simple test to update status"""
    print("=== Simple Status Update Test ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Update status to "In Progress" (commonly status_id=2)
            print("Updating issue #101 status to 'In Progress' (status_id=2)...")
            
            update_result = scraper.update_issue(
                "101", 
                status_id="2",
                notes="Status changed to In Progress via MCP test"
            )
            
            print(f"Update result: {json.dumps(update_result, indent=2)}")
            
            if update_result.get('success'):
                print("[OK] Update successful!")
                print(f"Updated fields: {update_result.get('updated_fields', [])}")
            else:
                print("[FAIL] Update failed")
                print(f"Error: {update_result.get('message')}")
            
            # Logout
            scraper.logout()
            print("[OK] Logged out")
        else:
            print("[FAIL] Login failed")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.logout()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(simple_status_update())
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

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
        
        # Authentication via browser
        print("\n[AUTH] Authentication Test:")
        print("Please login via browser when prompted")
        
        print(f"\n[LOGIN] Attempting login with Selenium (browser authentication)")
        login_result = scraper.login("", "")
        
        print(f"Login Result: {json.dumps(login_result, indent=2)}")
        
        if login_result.get('success'):
            # Test projects
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
            
            # Test issue search
            print("\n[SEARCH] Testing issue search functionality...")
            
            # Test 1: Basic search
            print("\n--- Test 1: Basic search (no filters) ---")
            search_result = scraper.search_issues()
            print(f"Basic search result: {json.dumps(search_result, indent=2)}")
            
            # Test 2: Text search
            print("\n--- Test 2: Text search ---")
            search_result = scraper.search_issues(q="test")
            print(f"Text search result: {json.dumps(search_result, indent=2)}")
            
            # Test 3: Status filter
            print("\n--- Test 3: Status filter ---")
            search_result = scraper.search_issues(status_id="open")
            print(f"Status search result: {json.dumps(search_result, indent=2)}")
            
            # Test 4: Pagination
            print("\n--- Test 4: Pagination ---")
            search_result = scraper.search_issues(page=1, per_page=5)
            print(f"Pagination search result: {json.dumps(search_result, indent=2)}")
            
            # Test 5: Get issue details
            if search_result.get('success') and search_result.get('issues'):
                first_issue = search_result['issues'][0]
                issue_id = first_issue['id']
                print(f"\n--- Test 5: Get issue details for #{issue_id} ---")
                details_result = scraper.get_issue_details(issue_id)
                print(f"Issue details result: {json.dumps(details_result, indent=2)}")
                
                # Test 6: Update issue (add a note)
                print(f"\n--- Test 6: Update issue #{issue_id} (add note) ---")
                update_result = scraper.update_issue(issue_id, notes="Test update from automated test")
                print(f"Update result: {json.dumps(update_result, indent=2)}")
            
            print("\n[LOGOUT] Logging out...")
            logout_result = scraper.logout()
            print(f"Logout Result: {json.dumps(logout_result, indent=2)}")
        else:
            print("[ERROR] Login failed, skipping tests")
        
        print("\n[DONE] All tests completed!")
        
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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for status validation functionality
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

async def test_status_validation():
    """Test status validation functionality"""
    print("=== Status Validation Test ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            issue_id = "101"
            
            # Test 1: Get available statuses
            print(f"\n--- Test 1: Get available statuses for issue #{issue_id} ---")
            statuses_result = scraper.get_available_statuses(issue_id)
            print(f"Available statuses result: {json.dumps(statuses_result, indent=2)}")
            
            if statuses_result.get('success'):
                available_statuses = statuses_result['statuses']
                print(f"Found {len(available_statuses)} available statuses:")
                for status in available_statuses:
                    print(f"  - {status['text']} (ID: {status['value']})")
                
                # Test 2: Try valid status update
                if available_statuses:
                    valid_status = available_statuses[0]  # Use first available status
                    print(f"\n--- Test 2: Update with valid status '{valid_status['text']}' ---")
                    update_result = scraper.update_issue(
                        issue_id, 
                        status_id=valid_status['value'],
                        notes="Testing valid status update"
                    )
                    print(f"Valid status update result: {json.dumps(update_result, indent=2)}")
                
                # Test 3: Try invalid status update
                print(f"\n--- Test 3: Update with invalid status '999' ---")
                invalid_update_result = scraper.update_issue(
                    issue_id, 
                    status_id="999",
                    notes="Testing invalid status update"
                )
                print(f"Invalid status update result: {json.dumps(invalid_update_result, indent=2)}")
                
                # Test 4: Try status update by name
                if available_statuses:
                    status_by_name = available_statuses[-1]  # Use last available status
                    print(f"\n--- Test 4: Update with status name '{status_by_name['text']}' ---")
                    name_update_result = scraper.update_issue(
                        issue_id, 
                        status_id=status_by_name['text'],
                        notes="Testing status update by name"
                    )
                    print(f"Status by name update result: {json.dumps(name_update_result, indent=2)}")
            
            # Logout
            scraper.logout()
            print("\n[OK] Logged out")
        else:
            print("[FAIL] Login failed")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.logout()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_status_validation())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for tracker search functionality
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

async def test_tracker_search():
    """Test searching issues by tracker"""
    print("=== Tracker Search Test ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Test tracker search with different values
            tracker_tests = [
                "課顁E,           # Japanese name
                "Bug",            # English name  
                "Feature",        # English name
                "Task",           # English name
                "1",              # ID
                "2",              # ID
                "3"               # ID
            ]
            
            for tracker in tracker_tests:
                print(f"\n--- Testing tracker: '{tracker}' ---")
                search_result = scraper.search_issues(tracker_id=tracker, per_page=5)
                
                if search_result.get('success'):
                    issues = search_result.get('issues', [])
                    total_count = search_result.get('total_count', 0)
                    print(f"Found {total_count} issues with tracker '{tracker}'")
                    
                    if issues:
                        print("Sample issues:")
                        for i, issue in enumerate(issues[:3], 1):  # Show first 3
                            print(f"  {i}. #{issue.get('id')} - {issue.get('subject', 'No subject')}")
                            if issue.get('tracker'):
                                print(f"     Tracker: {issue['tracker']}")
                    else:
                        print("No issues found for this tracker")
                else:
                    print(f"Search failed: {search_result.get('message')}")
            
            # Logout
            scraper.logout()
            print("\n[OK] Logged out")
        else:
            print("[FAIL] Login failed")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.logout()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_tracker_search())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for tracker validation functionality
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

async def test_tracker_validation():
    """Test tracker validation functionality"""
    print("=== Tracker Validation Test ===")
    
    scraper = RedmineSeleniumScraper()
    
    try:
        # Login
        print("Logging in...")
        login_result = scraper.login("", "")
        
        if login_result.get('success'):
            print("[OK] Login successful")
            
            # Test 1: Get available trackers
            print(f"\n--- Test 1: Get available trackers ---")
            trackers_result = scraper.get_available_trackers()
            print(f"Available trackers result: {json.dumps(trackers_result, indent=2)}")
            
            if trackers_result.get('success'):
                available_trackers = trackers_result['trackers']
                print(f"Found {len(available_trackers)} available trackers:")
                for tracker in available_trackers:
                    print(f"  - {tracker['text']} (ID: {tracker['value']})")
                
                # Test 2: Search with valid tracker ID
                if available_trackers:
                    valid_tracker = available_trackers[0]
                    print(f"\n--- Test 2: Search with valid tracker ID '{valid_tracker['value']}' ---")
                    search_result = scraper.search_issues(tracker_id=valid_tracker['value'], per_page=5)
                    print(f"Valid tracker search - Success: {search_result.get('success')}, Count: {search_result.get('total_count', 0)}")
                
                # Test 3: Search with valid tracker name
                if available_trackers:
                    valid_tracker = available_trackers[0]
                    print(f"\n--- Test 3: Search with valid tracker name '{valid_tracker['text']}' ---")
                    search_result = scraper.search_issues(tracker_id=valid_tracker['text'], per_page=5)
                    print(f"Valid tracker name search - Success: {search_result.get('success')}, Count: {search_result.get('total_count', 0)}")
                
                # Test 4: Search with invalid tracker
                print(f"\n--- Test 4: Search with invalid tracker 'InvalidTracker' ---")
                invalid_search_result = scraper.search_issues(tracker_id="InvalidTracker", per_page=5)
                print(f"Invalid tracker search result: {json.dumps(invalid_search_result, indent=2)}")
                
                # Test 5: Search with invalid tracker ID
                print(f"\n--- Test 5: Search with invalid tracker ID '999' ---")
                invalid_id_search_result = scraper.search_issues(tracker_id="999", per_page=5)
                print(f"Invalid tracker ID search result: {json.dumps(invalid_id_search_result, indent=2)}")
            
            # Logout
            scraper.logout()
            print("\n[OK] Logged out")
        else:
            print("[FAIL] Login failed")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            scraper.logout()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_tracker_validation())
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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
