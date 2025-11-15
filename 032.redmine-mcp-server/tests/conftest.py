"""
pytest configuration and fixtures for Redmine MCP Server tests
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from dotenv import load_dotenv

# Load environment variables from .env file (explicit path to ensure it loads)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def mock_scraper():
    """Mock RedmineSeleniumScraper for testing"""
    scraper = Mock()
    scraper.is_authenticated = False
    scraper.login = Mock(return_value={'success': True, 'message': 'Login successful'})
    scraper.logout = Mock(return_value={'success': True, 'message': 'Logout successful'})
    scraper.get_projects = Mock(return_value={
        'success': True,
        'message': 'Found 1 project',
        'projects': [{'id': 'test', 'name': 'Test Project', 'description': '', 'url': ''}]
    })
    scraper.search_issues = Mock(return_value={
        'success': True,
        'message': 'Found 1 issue',
        'issues': [{'id': '1', 'subject': 'Test Issue'}],
        'total_count': 1,
        'page': 1,
        'per_page': 25,
        'total_pages': 1
    })
    scraper.get_issue_details = Mock(return_value={
        'success': True,
        'message': 'Issue details retrieved',
        'issue': {'id': '1', 'subject': 'Test Issue', 'status': 'New'}
    })
    scraper.create_issue = Mock(return_value={
        'success': True,
        'message': 'Issue created',
        'issue_id': '123',
        'issue_url': 'http://test/issues/123'
    })
    scraper.update_issue = Mock(return_value={
        'success': True,
        'message': 'Issue updated',
        'updated_fields': ['status']
    })
    scraper.get_available_trackers = Mock(return_value={
        'success': True,
        'message': 'Found trackers',
        'trackers': [{'value': '1', 'text': 'Bug'}]
    })
    scraper.get_project_members = Mock(return_value={
        'success': True,
        'message': 'Found members',
        'members': [{'id': '1', 'name': 'Test User', 'roles': ['Developer']}]
    })
    return scraper

@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    config = Mock()
    config.base_url = 'http://localhost:3000'
    config.login_url = 'http://localhost:3000/login'
    config.projects_url = 'http://localhost:3000/projects'
    config.debug = False
    return config

@pytest.fixture(autouse=True, scope="function")
def mock_selenium_driver(request):
    """Automatically mock selenium driver creation to prevent browser launch.
    
    Skips mocking for integration tests so they can use real browsers.
    """
    # Check if test is marked with @pytest.mark.integration
    if request.node.get_closest_marker('integration'):
        # Skip mocking for integration tests
        yield None
        return
    
    with patch('redmine_selenium.webdriver.Chrome') as mock_chrome:
        mock_driver = Mock()
        mock_driver.get = Mock()
        mock_driver.quit = Mock()
        mock_driver.current_url = 'http://localhost:3000'
        mock_driver.page_source = 'test page'
        # Create a mock element that behaves like a real WebElement for common calls
        mock_element = Mock()
        mock_element.get_attribute = Mock(return_value='')
        mock_element.text = ''
        mock_element.find_elements = Mock(return_value=[])
        mock_element.find_element = Mock(return_value=mock_element)

        # Driver find_element should return the mock element; find_elements returns empty list
        mock_driver.find_element = Mock(return_value=mock_element)
        mock_driver.find_elements = Mock(return_value=[])
        mock_chrome.return_value = mock_driver
        yield mock_driver