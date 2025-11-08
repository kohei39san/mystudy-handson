"""
Unit tests for Redmine MCP Server
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from mcp.types import TextContent

# Import the module under test
from redmine_mcp_server import RedmineMCPServer


class TestRedmineMCPServer:
    """Test cases for RedmineMCPServer"""

    def test_server_initialization(self):
        """Test server initialization"""
        server = RedmineMCPServer()
        assert server.server is not None
        assert server.scraper is not None

    @pytest.mark.asyncio
    async def test_handle_login_success(self, mock_scraper):
        """Test successful login"""
        server = RedmineMCPServer()
        server.scraper = mock_scraper
        
        result = await server._handle_login({'username': 'test', 'password': 'test'})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert 'success' in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_handle_login_missing_params(self):
        """Test login with missing parameters"""
        server = RedmineMCPServer()
        
        result = await server._handle_login({'username': 'test'})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert 'error' in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_handle_get_projects_authenticated(self, mock_scraper):
        """Test get projects when authenticated"""
        server = RedmineMCPServer()
        server.scraper = mock_scraper
        server.scraper.is_authenticated = True
        
        result = await server._handle_get_projects({})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert 'success' in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_handle_get_projects_not_authenticated(self):
        """Test get projects when not authenticated"""
        server = RedmineMCPServer()
        server.scraper = Mock()
        server.scraper.is_authenticated = False
        
        result = await server._handle_get_projects({})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert 'error' in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_handle_search_issues(self, mock_scraper):
        """Test search issues"""
        server = RedmineMCPServer()
        server.scraper = mock_scraper
        server.scraper.is_authenticated = True
        
        result = await server._handle_search_issues({'project_id': 'test'})
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_scraper.search_issues.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_get_issue_details(self, mock_scraper):
        """Test get issue details"""
        server = RedmineMCPServer()
        server.scraper = mock_scraper
        server.scraper.is_authenticated = True
        
        result = await server._handle_get_issue_details({'issue_id': '1'})
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_scraper.get_issue_details.assert_called_once_with('1')

    @pytest.mark.asyncio
    async def test_handle_create_issue(self, mock_scraper):
        """Test create issue"""
        server = RedmineMCPServer()
        server.scraper = mock_scraper
        server.scraper.is_authenticated = True
        
        # Mock validation methods
        with patch.object(server.scraper, '_validate_tracker_for_project', return_value={'valid': True}):
            with patch.object(server.scraper, '_validate_fields', return_value={'valid': True}):
                result = await server._handle_create_issue({
                    'project_id': 'test',
                    'issue_tracker_id': '1',
                    'issue_subject': 'Test Issue'
                })
        
        assert isinstance(result, list)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_handle_update_issue(self, mock_scraper):
        """Test update issue"""
        server = RedmineMCPServer()
        server.scraper = mock_scraper
        server.scraper.is_authenticated = True
        
        result = await server._handle_update_issue({
            'issue_id': '1',
            'fields': {'status_id': '2', 'notes': 'Test update'}
        })
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_scraper.update_issue.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_get_project_members(self, mock_scraper):
        """Test get project members"""
        server = RedmineMCPServer()
        server.scraper = mock_scraper
        server.scraper.is_authenticated = True
        
        result = await server._handle_get_project_members({'project_id': 'test'})
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_scraper.get_project_members.assert_called_once_with('test')

    @pytest.mark.asyncio
    async def test_handle_logout(self, mock_scraper):
        """Test logout"""
        server = RedmineMCPServer()
        server.scraper = mock_scraper
        
        result = await server._handle_logout({})
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_scraper.logout.assert_called_once()