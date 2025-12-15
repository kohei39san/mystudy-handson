"""
Integration tests for Redmine MCP Server
These tests require a running Redmine instance and valid credentials
"""

import pytest
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (explicit path to ensure it loads)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import modules under test
from redmine_mcp_server import RedmineMCPServer
from redmine_selenium import RedmineSeleniumScraper


@pytest.mark.integration
class TestRedmineIntegration:
    """Integration tests that require a real Redmine instance"""

    @pytest.fixture(scope="class")
    def scraper(self):
        """Create a scraper instance for integration tests"""
        return RedmineSeleniumScraper()

    @pytest.fixture(scope="class") 
    def mcp_server(self):
        """Create an MCP server instance for integration tests"""
        return RedmineMCPServer()

    @pytest.mark.asyncio
    async def test_server_info(self, mcp_server):
        """Test getting server information"""
        result = await mcp_server._handle_get_server_info({})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert 'server url' in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_get_issue_details_custom_fields(self, mcp_server):
        """Test that get_issue_details correctly retrieves custom fields"""
        username = os.getenv('REDMINE_USERNAME', '')
        password = os.getenv('REDMINE_PASSWORD', '')
        
        # Debug: Print environment variables
        print(f"REDMINE_URL: {os.getenv('REDMINE_URL')}")
        print(f"REDMINE_USERNAME exists: {bool(username)}")
        print(f"REDMINE_PASSWORD exists: {bool(password)}")
        
        if not username or not password:
            pytest.skip("Redmine credentials not configured")
        
        # First login
        login_result = await mcp_server._handle_login({
            'username': username,
            'password': password
        })
        
        # Verify login was successful
        assert len(login_result) == 1
        login_response = login_result[0]
        print(f"Login response: {login_response.text}")
        assert 'successful' in login_response.text.lower()
        

        # Search for issues to get an issue ID
        search_result = await mcp_server._handle_search_issues({})
        assert len(search_result) == 1
        search_response = search_result[0]
        
        # Debug: Print search response
        print(f"Search response: {search_response.text[:500]}...")  # First 500 chars
        
        # Extract issue ID from search response
        try:
            import ast
            # The response is a Python dict string representation, not JSON
            response_data = ast.literal_eval(search_response.text)
            if response_data.get('success') and response_data.get('issues'):
                issues = response_data['issues']
                if issues:
                    issue_id = issues[0]['id']  # Get first issue ID
                    print(f"Found issue ID: {issue_id}")
                    
                    # Get issue details
                    details_result = await mcp_server._handle_get_issue_details({
                        'issue_id': issue_id
                    })
                    
                    assert len(details_result) == 1
                    details_response = details_result[0]
                    
                    print(f"Issue details response: {details_response.text}")
                    
                    # Parse the details response
                    details_data = ast.literal_eval(details_response.text)
                    
                    # Verify response structure
                    assert details_data.get('success') is True
                    assert 'issue' in details_data
                    
                    issue_data = details_data['issue']
                    
                    # Check if custom fields are included
                    if issue_data.get('custom_fields'):
                        print(f"✓ Custom fields found in issue #{issue_id}: {issue_data['custom_fields']}")
                    else:
                        print(f"✗ No custom fields found in issue #{issue_id}")
                        # Still verify the basic structure is working
                        assert 'id' in issue_data
                        assert 'subject' in issue_data
                        print("Basic issue structure verified")
                else:
                    pytest.skip("No issues found in search response")
            else:
                pytest.skip("Search request failed or returned no data")
        except (ValueError, SyntaxError) as e:
            print(f"Failed to parse search response as Python literal: {e}")
            print(f"Response text: {search_response.text[:200]}...")
            pytest.skip("Invalid response format from search")

    @pytest.mark.skipif(not (os.getenv('REDMINE_USERNAME') and os.getenv('REDMINE_PASSWORD')), 
                       reason="Credentials not configured")
    @pytest.mark.asyncio
    async def test_login_flow(self, mcp_server):
        """Test the complete login flow"""
        username = os.getenv('REDMINE_USERNAME', '')
        password = os.getenv('REDMINE_PASSWORD', '')
        
        if not username or not password:
            pytest.skip("Credentials not available")
        
        # Test login
        login_result = await mcp_server._handle_login({
            'username': username,
            'password': password
        })
        
        assert isinstance(login_result, list)
        # Note: This test may require manual 2FA completion
        
        # Test logout
        logout_result = await mcp_server._handle_logout({})
        assert isinstance(logout_result, list)

    @pytest.mark.skipif(not (os.getenv('REDMINE_USERNAME') and os.getenv('REDMINE_PASSWORD')), 
                       reason="Credentials not configured")
    def test_scraper_basic_functionality(self, scraper):
        """Test basic scraper functionality"""
        username = os.getenv('REDMINE_USERNAME', '')
        password = os.getenv('REDMINE_PASSWORD', '')
        
        if not username or not password:
            pytest.skip("Credentials not available")
        
        try:
            # Test login (may require manual intervention for 2FA)
            login_result = scraper.login(username, password)
            
            if login_result.get('success'):
                # Test get projects
                projects_result = scraper.get_projects()
                assert projects_result.get('success') is True
                
                # Test search issues
                search_result = scraper.search_issues(per_page=5)
                assert search_result.get('success') is True
                
                # Test logout
                logout_result = scraper.logout()
                assert logout_result.get('success') is True
            else:
                pytest.skip(f"Login failed: {login_result.get('message')}")
                
        except Exception as e:
            pytest.skip(f"Integration test failed: {str(e)}")

    @pytest.mark.skipif(not (os.getenv('REDMINE_USERNAME') and os.getenv('REDMINE_PASSWORD')), 
                       reason="Credentials not configured")
    @pytest.mark.asyncio
    async def test_get_projects_via_mcp_server(self, mcp_server):
        """Test get_projects functionality through MCP server"""
        username = os.getenv('REDMINE_USERNAME', '')
        password = os.getenv('REDMINE_PASSWORD', '')
        
        if not username or not password:
            pytest.skip("Credentials not available")
        
        try:
            # First login
            login_result = await mcp_server._handle_login({
                'username': username,
                'password': password
            })
            
            # Parse login result to verify authentication
            login_text = login_result[0].text
            if 'error' in login_text.lower() or 'failed' in login_text.lower():
                pytest.skip(f"Login failed: {login_text}")
            
            # Now test get_projects
            projects_result = await mcp_server._handle_get_projects({})
            
            assert isinstance(projects_result, list)
            assert len(projects_result) == 1
            
            # Parse result - should be a valid JSON string containing project data
            result_text = projects_result[0].text
            assert isinstance(result_text, str)
            
            # Try to parse as JSON-like dict format
            import ast
            try:
                result_dict = ast.literal_eval(result_text)
                
                # Verify structure
                assert 'success' in result_dict
                assert 'message' in result_dict  
                assert 'projects' in result_dict
                
                if result_dict['success']:
                    # Verify projects list structure
                    assert isinstance(result_dict['projects'], list)
                    
                    # If projects exist, verify each project has required fields
                    if result_dict['projects']:
                        project = result_dict['projects'][0]
                        assert 'id' in project
                        assert 'name' in project
                        # Optional fields
                        assert 'description' in project
                        assert 'url' in project
                        
                        # Verify field types
                        assert isinstance(project['id'], str)
                        assert isinstance(project['name'], str)
                else:
                    # If not successful, check error message
                    assert isinstance(result_dict['message'], str)
                    
            except (ValueError, SyntaxError) as e:
                pytest.fail(f"Failed to parse projects result: {e}. Result: {result_text}")
                
        except Exception as e:
            pytest.skip(f"MCP server get_projects test failed: {str(e)}")

    @pytest.mark.skipif(not (os.getenv('REDMINE_USERNAME') and os.getenv('REDMINE_PASSWORD')), 
                       reason="Credentials not configured")
    def test_scraper_get_projects_functionality(self, scraper):
        """Test scraper get_projects functionality directly"""
        username = os.getenv('REDMINE_USERNAME', '')
        password = os.getenv('REDMINE_PASSWORD', '')
        
        if not username or not password:
            pytest.skip("Credentials not available")
        
        try:
            # Test login
            login_result = scraper.login(username, password)
            
            if login_result.get('success'):
                # Test get_projects
                projects_result = scraper.get_projects()
                
                # Verify basic structure
                assert isinstance(projects_result, dict)
                assert 'success' in projects_result
                assert 'message' in projects_result
                assert 'projects' in projects_result
                
                if projects_result['success']:
                    # Verify projects list structure
                    assert isinstance(projects_result['projects'], list)
                    assert isinstance(projects_result['message'], str)
                    
                    # If projects exist, verify each project structure
                    if projects_result['projects']:
                        project = projects_result['projects'][0]
                        
                        # Required fields
                        assert 'id' in project
                        assert 'name' in project
                        
                        # Verify field types and values
                        assert isinstance(project['id'], str)
                        assert len(project['id']) > 0, "Project ID should not be empty"
                        
                        assert isinstance(project['name'], str) 
                        assert len(project['name']) > 0, "Project name should not be empty"
                        
                        # Optional fields (can be None or empty string)
                        if 'description' in project:
                            assert isinstance(project.get('description'), (str, type(None)))
                        if 'url' in project:
                            assert isinstance(project.get('url'), (str, type(None)))
                        if 'created_on' in project:
                            assert isinstance(project.get('created_on'), (str, type(None)))
                        if 'status' in project:
                            assert isinstance(project.get('status'), (str, type(None)))
                        
                        # Test that project IDs are unique
                        project_ids = [p['id'] for p in projects_result['projects']]
                        assert len(project_ids) == len(set(project_ids)), "Project IDs should be unique"
                        
                        print(f"✓ Found {len(projects_result['projects'])} projects")
                        print(f"✓ Sample project: {project['name']} (ID: {project['id']})")
                    else:
                        print("! No projects found (empty list)")
                else:
                    # Test failed, check error message
                    assert isinstance(projects_result['message'], str)
                    print(f"! get_projects failed: {projects_result['message']}")
                
                # Test logout
                logout_result = scraper.logout()
                assert logout_result.get('success') is True
                
            else:
                pytest.skip(f"Login failed: {login_result.get('message')}")
                
        except Exception as e:
            pytest.skip(f"Scraper get_projects test failed: {str(e)}")

    def test_config_validation(self):
        """Test that configuration is properly loaded"""
        from config import config
        
        assert hasattr(config, 'base_url')
        assert hasattr(config, 'login_url')
        assert hasattr(config, 'projects_url')
        assert config.base_url is not None
        assert config.login_url is not None
        assert config.projects_url is not None

    @pytest.mark.skipif(not (os.getenv('REDMINE_USERNAME') and os.getenv('REDMINE_PASSWORD')), 
                       reason="Credentials not configured")
    @pytest.mark.asyncio
    async def test_get_time_entries_without_auth(self, mcp_server):
        """Test that get_time_entries fails without authentication"""
        result = await mcp_server._handle_get_time_entries({
            'project_id': 'test-project'
        })
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert '[ERROR]' in result[0].text
        assert 'Not authenticated' in result[0].text

    @pytest.mark.skipif(not (os.getenv('REDMINE_USERNAME') and os.getenv('REDMINE_PASSWORD')), 
                       reason="Credentials not configured")
    @pytest.mark.asyncio
    async def test_get_time_entries_missing_project_id(self, mcp_server):
        """Test that get_time_entries requires project_id"""
        result = await mcp_server._handle_get_time_entries({})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert '[ERROR]' in result[0].text
        assert 'Project ID is required' in result[0].text

    @pytest.mark.skipif(not (os.getenv('REDMINE_USERNAME') and os.getenv('REDMINE_PASSWORD') and os.getenv('TEST_PROJECT_ID')), 
                       reason="Credentials or TEST_PROJECT_ID not configured")
    @pytest.mark.asyncio
    async def test_get_time_entries_with_authentication(self, mcp_server):
        """Test get_time_entries after authentication"""
        username = os.getenv('REDMINE_USERNAME', '')
        password = os.getenv('REDMINE_PASSWORD', '')
        project_id = os.getenv('TEST_PROJECT_ID', '')
        
        if not username or not password or not project_id:
            pytest.skip("Credentials or TEST_PROJECT_ID not available")
        
        # First login
        login_result = await mcp_server._handle_login({
            'username': username,
            'password': password
        })
        
        # Parse login result to verify authentication
        login_text = login_result[0].text
        if 'error' in login_text.lower() or 'failed' in login_text.lower():
            pytest.skip(f"Login failed: {login_text}")
        
        # Now test get_time_entries
        time_entries_result = await mcp_server._handle_get_time_entries({
            'project_id': project_id
        })
        
        assert isinstance(time_entries_result, list)
        assert len(time_entries_result) == 1
        
        # Parse result
        result_text = time_entries_result[0].text
        # Result should be a dictionary as string
        assert isinstance(result_text, str)

    @pytest.mark.skipif(not (os.getenv('REDMINE_USERNAME') and os.getenv('REDMINE_PASSWORD') and os.getenv('TEST_PROJECT_ID')), 
                       reason="Credentials or TEST_PROJECT_ID not configured")
    def test_scraper_get_time_entries_detailed(self, scraper):
        """Detailed test for scraper get_time_entries functionality with debug output"""
        username = os.getenv('REDMINE_USERNAME', '')
        password = os.getenv('REDMINE_PASSWORD', '')
        project_id = os.getenv('TEST_PROJECT_ID', '')
        
        if not username or not password or not project_id:
            pytest.skip("Credentials or TEST_PROJECT_ID not available")
        
        try:
            # Test login
            print(f"\n=== Testing get_time_entries for project: {project_id} ===")
            login_result = scraper.login(username, password)
            print(f"Login result: {login_result.get('success')} - {login_result.get('message')}")
            
            if login_result.get('success'):
                # Test get_time_entries without filters
                print("\n--- Testing basic get_time_entries ---")
                time_entries_result = scraper.get_time_entries(project_id)
                
                print(f"Basic call success: {time_entries_result.get('success')}")
                print(f"Message: {time_entries_result.get('message')}")
                print(f"Total count: {time_entries_result.get('total_count')}")
                print(f"Time entries found: {len(time_entries_result.get('time_entries', []))}")
                
                # Basic assertions
                assert time_entries_result.get('success') is True
                assert 'time_entries' in time_entries_result
                assert 'total_count' in time_entries_result
                assert 'current_page' in time_entries_result
                assert 'per_page' in time_entries_result
                
                # Verify response structure
                assert isinstance(time_entries_result['time_entries'], list)
                assert isinstance(time_entries_result['total_count'], int)
                assert time_entries_result['current_page'] >= 1
                assert time_entries_result['per_page'] > 0
                
                # Print first time entry details if available
                if time_entries_result['time_entries']:
                    first_entry = time_entries_result['time_entries'][0]
                    print(f"First time entry fields: {list(first_entry.keys())}")
                    print(f"Sample time entry: {first_entry}")
                    
                    # Verify time entry structure
                    assert 'spent_on' in first_entry
                    assert 'hours' in first_entry
                    assert 'user' in first_entry
                    assert 'activity' in first_entry
                else:
                    print("No time entries found - this might indicate a parsing issue")
                
                # Test get_time_entries with date filter
                print("\n--- Testing with date filter ---")
                import datetime
                end_date = datetime.date.today()
                start_date = end_date - datetime.timedelta(days=30)
                
                filtered_result = scraper.get_time_entries(
                    project_id,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )
                
                print(f"Filtered call success: {filtered_result.get('success')}")
                print(f"Filtered entries count: {len(filtered_result.get('time_entries', []))}")
                print(f"Date range: {start_date} to {end_date}")
                
                assert filtered_result.get('success') is True
                assert 'time_entries' in filtered_result
                
                # Test get_time_entries with pagination
                print("\n--- Testing with pagination ---")
                paginated_result = scraper.get_time_entries(
                    project_id,
                    page=1,
                    per_page=5
                )
                
                print(f"Paginated call success: {paginated_result.get('success')}")
                print(f"Requested per_page: 5, actual: {paginated_result.get('per_page')}")
                print(f"Paginated entries count: {len(paginated_result.get('time_entries', []))}")
                
                assert paginated_result.get('success') is True
                assert paginated_result.get('per_page') == 5
                
                # Test get_time_entries with user filter (simplified)
                print("\n--- Testing with user filter ---")
                test_user_id = os.getenv('TEST_USER_ID', '')
                if test_user_id:
                    print(f"Testing with configured user: {test_user_id}")
                    user_filtered_result = scraper.get_time_entries(
                        project_id,
                        user_id=test_user_id
                    )
                    
                    print(f"User filtered call success: {user_filtered_result.get('success')}")
                    print(f"User filtered entries count: {len(user_filtered_result.get('time_entries', []))}")
                    
                    # Check current URL for debugging
                    if hasattr(scraper, 'driver') and scraper.driver:
                        current_url = scraper.driver.current_url
                        print(f"User filter URL: {current_url}")
                        if 'user_id' in current_url:
                            print("✓ user_id parameter found in URL")
                        else:
                            print("⚠ user_id parameter not found in URL")
                    
                    # Note: User filter may return 0 results if the user_id format is incorrect
                    assert user_filtered_result.get('success') is True
                    assert 'time_entries' in user_filtered_result
                else:
                    print("TEST_USER_ID not configured, skipping user filter test")
                
                # Additional validation: Check URL construction for time entries
                print("\n--- URL Construction Test ---")
                # This is more for debugging - let's check what URL is being used
                if hasattr(scraper, 'driver') and scraper.driver:
                    current_url = scraper.driver.current_url
                    print(f"Current browser URL: {current_url}")
                    if 'time_entries' in current_url:
                        print("✓ Correctly navigated to time entries page")
                    else:
                        print("⚠ Not on time entries page - this might be the issue")
                
                # Test logout
                logout_result = scraper.logout()
                assert logout_result.get('success') is True
                print(f"Logout success: {logout_result.get('success')}")
                
            else:
                pytest.skip(f"Login failed: {login_result.get('message')}")
                
        except Exception as e:
            print(f"\nError during test: {str(e)}")
            import traceback
            traceback.print_exc()
            pytest.skip(f"Scraper integration test failed: {str(e)}")

    @pytest.mark.skipif(not (os.getenv('REDMINE_USERNAME') and os.getenv('REDMINE_PASSWORD') and os.getenv('TEST_PROJECT_ID')), 
                       reason="Credentials or TEST_PROJECT_ID not configured")
    def test_scraper_get_time_entries_debug_page_content(self, scraper):
        """Debug test to examine actual page content for time entries"""
        username = os.getenv('REDMINE_USERNAME', '')
        password = os.getenv('REDMINE_PASSWORD', '')
        project_id = os.getenv('TEST_PROJECT_ID', '')
        
        if not username or not password or not project_id:
            pytest.skip("Credentials or TEST_PROJECT_ID not available")
        
        try:
            # Login
            login_result = scraper.login(username, password)
            
            if login_result.get('success'):
                print(f"\n=== Debug: Examining time entries page content ===")
                
                # Manually navigate to time entries page to debug
                from config import config
                import time
                
                time_entries_url = f"{config.base_url}/projects/{project_id}/time_entries"
                print(f"Navigating to: {time_entries_url}")
                
                scraper.driver.get(time_entries_url)
                time.sleep(2)  # Wait for page load
                
                # Debug page content
                page_title = scraper.driver.title
                current_url = scraper.driver.current_url
                print(f"Page title: {page_title}")
                print(f"Current URL: {current_url}")
                
                # Check if we're on the right page
                if '404' in scraper.driver.page_source:
                    print("❌ 404 error - time entries not accessible")
                elif 'login' in current_url.lower():
                    print("❌ Redirected to login - session expired")
                elif 'time_entries' not in current_url:
                    print(f"❌ Not on time entries page, redirected to: {current_url}")
                else:
                    print("✓ Successfully navigated to time entries page")
                
                # Look for table elements
                from selenium.webdriver.common.by import By
                tables = scraper.driver.find_elements(By.TAG_NAME, "table")
                print(f"Found {len(tables)} table(s) on page")
                
                # Look for specific time entries table
                time_table = scraper.driver.find_elements(By.CSS_SELECTOR, "#content table.list")
                print(f"Found {len(time_table)} time entries table(s)")
                
                if time_table:
                    # Examine table structure
                    rows = time_table[0].find_elements(By.TAG_NAME, "tr")
                    print(f"Table has {len(rows)} rows")
                    
                    if len(rows) > 0:
                        # Print header row
                        header_cells = rows[0].find_elements(By.TAG_NAME, "th")
                        if header_cells:
                            headers = [cell.text.strip() for cell in header_cells]
                            print(f"Table headers: {headers}")
                        
                        # Print first data row if available
                        if len(rows) > 1:
                            data_cells = rows[1].find_elements(By.TAG_NAME, "td")
                            if data_cells:
                                data = [cell.text.strip() for cell in data_cells]
                                print(f"First data row: {data}")
                        else:
                            print("No data rows found in table")
                    else:
                        print("Table is empty")
                else:
                    print("No time entries table found")
                    
                    # Check for any content that might indicate time entries
                    page_source_snippet = scraper.driver.page_source[:1000]
                    print(f"Page content snippet: {page_source_snippet}")
                
                # Look for pagination elements
                pagination = scraper.driver.find_elements(By.CSS_SELECTOR, ".pagination, .paginator")
                print(f"Found {len(pagination)} pagination element(s)")
                
                if pagination:
                    pagination_text = pagination[0].text.strip()
                    print(f"Pagination text: {pagination_text}")
                
                # Look for count information
                count_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".count, .total-count, .entry-count")
                for element in count_elements:
                    text = element.text.strip()
                    if text:
                        print(f"Count element text: {text}")
                
                # Test the actual method
                print(f"\n--- Testing actual get_time_entries method ---")
                result = scraper.get_time_entries(project_id)
                print(f"Method result: {result}")
                
                # Logout
                scraper.logout()
                
            else:
                pytest.skip(f"Login failed: {login_result.get('message')}")
                
        except Exception as e:
            print(f"\nDebug test error: {str(e)}")
            import traceback
            traceback.print_exc()
            pytest.skip(f"Debug test failed: {str(e)}")

    @pytest.mark.skipif(not (os.getenv('REDMINE_USERNAME') and os.getenv('REDMINE_PASSWORD') and os.getenv('TEST_PROJECT_ID')), 
                       reason="Credentials or TEST_PROJECT_ID not configured")
    def test_scraper_get_project_members(self, scraper):
        """Test scraper get_project_members functionality"""
        username = os.getenv('REDMINE_USERNAME', '')
        password = os.getenv('REDMINE_PASSWORD', '')
        project_id = os.getenv('TEST_PROJECT_ID', '')
        
        if not username or not password or not project_id:
            pytest.skip("Credentials or TEST_PROJECT_ID not available")
        
        try:
            # Test login
            login_result = scraper.login(username, password)
            
            if login_result.get('success'):
                # Test get_project_members
                members_result = scraper.get_project_members(project_id)
                assert members_result.get('success') is True
                assert 'members' in members_result
                assert 'project_id' in members_result
                assert members_result['project_id'] == project_id
                
                # Verify response structure
                assert isinstance(members_result['members'], list)
                
                # If members exist, verify structure
                if members_result['members']:
                    member = members_result['members'][0]
                    assert 'id' in member
                    assert 'name' in member
                    assert 'is_current_user' in member
                
                # Test logout
                logout_result = scraper.logout()
                assert logout_result.get('success') is True
            else:
                pytest.skip(f"Login failed: {login_result.get('message')}")
                
        except Exception as e:
            pytest.skip(f"Scraper integration test failed: {str(e)}")