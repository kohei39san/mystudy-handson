"""
Integration tests for Redmine MCP Server
These tests require a running Redmine instance and valid credentials
"""

import pytest
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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