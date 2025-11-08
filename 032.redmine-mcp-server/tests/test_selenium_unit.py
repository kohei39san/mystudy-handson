"""
Unit tests for Redmine Selenium Scraper
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Import the module under test
from redmine_selenium import RedmineSeleniumScraper


class TestRedmineSeleniumScraper:
    """Test cases for RedmineSeleniumScraper"""

    def test_scraper_initialization(self):
        """Test scraper initialization"""
        scraper = RedmineSeleniumScraper()
        assert scraper.driver is None
        assert scraper.is_authenticated is False
        assert scraper.headless_mode is False

    @patch('redmine_selenium.webdriver.Chrome')
    @patch('redmine_selenium.ChromeDriverManager')
    def test_create_driver(self, mock_driver_manager, mock_chrome):
        """Test driver creation"""
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        scraper = RedmineSeleniumScraper()
        driver = scraper._create_driver(headless=True)
        
        assert driver is not None
        mock_chrome.assert_called_once()

    @patch('redmine_selenium.RedmineSeleniumScraper._create_driver')
    def test_login_missing_credentials(self, mock_create_driver):
        """Test login with missing credentials"""
        mock_driver = Mock()
        mock_create_driver.return_value = mock_driver
        
        scraper = RedmineSeleniumScraper()
        
        # Mock empty credentials should not trigger browser
        with patch.object(scraper, '_create_driver', return_value=mock_driver):
            # Test should pass without actual browser interaction
            result = scraper.login("", "password")
            # Since we're mocking, we expect it to proceed but fail validation
            assert 'username' in str(result).lower() or 'password' in str(result).lower()

    @patch('redmine_selenium.RedmineSeleniumScraper._create_driver')
    def test_login_form_not_found(self, mock_create_driver):
        """Test login when form is not found"""
        mock_driver = Mock()
        mock_driver.get = Mock()
        mock_driver.find_element.side_effect = NoSuchElementException()
        mock_create_driver.return_value = mock_driver
        
        scraper = RedmineSeleniumScraper()
        result = scraper.login("test", "test")
        
        assert result['success'] is False
        assert 'timeout' in result['message'].lower()

    def test_get_projects_not_authenticated(self):
        """Test get projects when not authenticated"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = False
        
        result = scraper.get_projects()
        
        assert result['success'] is False
        assert 'not authenticated' in result['message'].lower()
        assert result['projects'] == []

    def test_get_projects_authenticated(self, mock_selenium_driver):
        """Test get projects when authenticated"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock page elements
        mock_table = Mock()
        mock_row = Mock()
        mock_cell = Mock()
        mock_link = Mock()
        
        mock_link.text = "Test Project"
        mock_link.get_attribute.return_value = "http://test/projects/test"
        mock_cell.find_element.return_value = mock_link
        mock_row.find_elements.return_value = [mock_cell]
        mock_table.find_elements.return_value = [Mock(), mock_row]  # Header + data row
        
        mock_selenium_driver.current_url = "http://test/projects"
        mock_selenium_driver.find_element.return_value = mock_table
        
        result = scraper.get_projects()
        
        assert result['success'] is True
        assert len(result['projects']) > 0

    def test_search_issues_not_authenticated(self):
        """Test search issues when not authenticated"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = False
        
        result = scraper.search_issues()
        
        assert result['success'] is False
        assert 'not authenticated' in result['message'].lower()

    def test_search_issues_authenticated(self, mock_selenium_driver):
        """Test search issues when authenticated"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        mock_selenium_driver.current_url = "http://test/issues"
        mock_selenium_driver.page_source = "issues page content"
        mock_selenium_driver.find_element.side_effect = NoSuchElementException()
        mock_selenium_driver.find_elements.return_value = []
        
        result = scraper.search_issues(q="test")
        
        assert result['success'] is True
        assert 'issues' in result

    def test_get_issue_details_not_authenticated(self):
        """Test get issue details when not authenticated"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = False
        
        result = scraper.get_issue_details("1")
        
        assert result['success'] is False
        assert 'not authenticated' in result['message'].lower()

    def test_get_issue_details_authenticated(self, mock_selenium_driver):
        """Test get issue details when authenticated"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        mock_selenium_driver.current_url = "http://test/issues/1"
        mock_selenium_driver.page_source = "issue details page"
        
        # Mock subject element
        mock_subject = Mock()
        mock_subject.text = "Test Issue"
        
        def mock_find_element(by, selector):
            if selector == ".subject h3":
                return mock_subject
            raise NoSuchElementException()
        
        mock_selenium_driver.find_element.side_effect = mock_find_element
        mock_selenium_driver.find_elements.return_value = []
        
        result = scraper.get_issue_details("1")
        
        assert result['success'] is True
        assert result['issue']['id'] == "1"

    def test_logout(self):
        """Test logout functionality"""
        scraper = RedmineSeleniumScraper()
        mock_driver = Mock()
        scraper.driver = mock_driver
        scraper.is_authenticated = True
        
        result = scraper.logout()
        
        assert result['success'] is True
        assert scraper.is_authenticated is False
        assert scraper.driver is None
        mock_driver.quit.assert_called_once()

    def test_validate_fields_missing_tracker_fields(self):
        """Test field validation when tracker fields cannot be retrieved"""
        scraper = RedmineSeleniumScraper()
        scraper.get_tracker_fields = Mock(return_value={'success': False, 'message': 'Error'})
        
        result = scraper._validate_fields("project1", "tracker1", {"field1": "value1"})
        
        assert result['valid'] is False

    def test_validate_fields_missing_required(self):
        """Test field validation with missing required fields"""
        scraper = RedmineSeleniumScraper()
        scraper.get_tracker_fields = Mock(return_value={
            'success': True,
            'fields': [
                {'id': 'required_field', 'name': 'Required Field', 'required': True},
                {'id': 'optional_field', 'name': 'Optional Field', 'required': False}
            ]
        })
        
        result = scraper._validate_fields("project1", "tracker1", {"optional_field": "value"})
        
        assert result['valid'] is False
        assert 'missing required fields' in result['message'].lower()

    def test_validate_assignee_empty_value(self):
        """Test assignee validation with empty value"""
        scraper = RedmineSeleniumScraper()
        
        result = scraper._validate_assignee("project1", "")
        
        assert result['valid'] is True

    def test_validate_assignee_valid_member(self):
        """Test assignee validation with valid member"""
        scraper = RedmineSeleniumScraper()
        scraper.get_project_members = Mock(return_value={
            'success': True,
            'members': [{'id': '1', 'name': 'Test User'}]
        })
        
        result = scraper._validate_assignee("project1", "1")
        
        assert result['valid'] is True

    def test_validate_assignee_invalid_member(self):
        """Test assignee validation with invalid member"""
        scraper = RedmineSeleniumScraper()
        scraper.get_project_members = Mock(return_value={
            'success': True,
            'members': [{'id': '1', 'name': 'Test User'}]
        })
        
        result = scraper._validate_assignee("project1", "999")
        
        assert result['valid'] is False
        assert 'not found' in result['message'].lower()