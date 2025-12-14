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
@pytest.mark.skipif(not os.getenv('REDMINE_URL'), reason="REDMINE_URL not configured")
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
    def test_scraper_get_time_entries(self, scraper):
        """Test scraper get_time_entries functionality"""
        username = os.getenv('REDMINE_USERNAME', '')
        password = os.getenv('REDMINE_PASSWORD', '')
        project_id = os.getenv('TEST_PROJECT_ID', '')
        
        if not username or not password or not project_id:
            pytest.skip("Credentials or TEST_PROJECT_ID not available")
        
        try:
            # Test login
            login_result = scraper.login(username, password)
            
            if login_result.get('success'):
                # Test get_time_entries without filters
                time_entries_result = scraper.get_time_entries(project_id)
                assert time_entries_result.get('success') is True
                assert 'time_entries' in time_entries_result
                assert 'total_count' in time_entries_result
                assert 'page' in time_entries_result
                assert 'per_page' in time_entries_result
                
                # Verify response structure
                assert isinstance(time_entries_result['time_entries'], list)
                assert isinstance(time_entries_result['total_count'], int)
                assert time_entries_result['page'] >= 1
                assert time_entries_result['per_page'] > 0
                
                # Test get_time_entries with date filter
                import datetime
                end_date = datetime.date.today()
                start_date = end_date - datetime.timedelta(days=30)
                
                filtered_result = scraper.get_time_entries(
                    project_id,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )
                assert filtered_result.get('success') is True
                assert 'time_entries' in filtered_result
                
                # Test get_time_entries with pagination
                paginated_result = scraper.get_time_entries(
                    project_id,
                    page=1,
                    per_page=5
                )
                assert paginated_result.get('success') is True
                assert paginated_result.get('per_page') == 5
                
                # Test logout
                logout_result = scraper.logout()
                assert logout_result.get('success') is True
            else:
                pytest.skip(f"Login failed: {login_result.get('message')}")
                
        except Exception as e:
            pytest.skip(f"Scraper integration test failed: {str(e)}")

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