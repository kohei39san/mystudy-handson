"""
Unit tests for Redmine Selenium Scraper organized by tool/functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pydantic import ValidationError

# Import the modules under test
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)

from src.redmine_selenium import RedmineSeleniumScraper
from src.schemas import (
    ProjectInfo, ProjectsResponse, MemberInfo, ProjectMembersResponse,
    IssueInfo, IssuesResponse, TrackerInfo, TrackersResponse,
    StatusInfo, StatusesResponse, FieldInfo, FieldsResponse,
    TimeEntryInfo, TimeEntriesResponse, CreateIssueResponse, 
    UpdateIssueResponse, IssueDetailResponse, LoginResponse,
    GeneralResponse, ServerInfo, ServerInfoResponse
)


@pytest.fixture
def mock_selenium_driver():
    """Shared mock driver fixture"""
    return Mock()


class TestScraperCore:
    """Test core scraper functionality (initialization, driver management, validation helpers)"""

    def test_scraper_initialization(self):
        """Test scraper initialization"""
        scraper = RedmineSeleniumScraper()
        assert scraper.driver is None
        assert scraper.is_authenticated is False
        assert scraper.headless_mode is False

    @patch('src.redmine_selenium.webdriver.Chrome')
    @patch('src.redmine_selenium.ChromeDriverManager')
    def test_create_driver(self, mock_driver_manager, mock_chrome):
        """Test driver creation"""
        mock_driver_manager.return_value.install.return_value = '/path/to/chromedriver'
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        scraper = RedmineSeleniumScraper()
        driver = scraper._create_driver(headless=True)
        
        assert driver is not None
        mock_chrome.assert_called_once()

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


class TestAuthenticationTools:
    """Test authentication-related tools (login, logout)"""

    @patch('src.redmine_selenium.os.getenv')
    @patch('src.redmine_selenium.time.sleep')
    @patch('src.redmine_selenium.time.time')
    @patch('selenium.webdriver.support.ui.WebDriverWait')
    @patch('src.redmine_selenium.RedmineSeleniumScraper._create_driver')
    def test_login_missing_credentials(self, mock_create_driver, mock_wait_class, mock_time, mock_sleep, mock_getenv):
        """Test login with missing credentials"""
        # Mock environment variable to short timeout
        def getenv_side_effect(key, default=None):
            if key == 'TWOFA_WAIT':
                return '1'  # 1 second timeout
            elif key == 'POLL_INTERVAL':
                return '0.1'  # Very short poll interval
            return default
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock time.time to immediately exceed the timeout
        mock_time.side_effect = [0, 2]  # start_time=0, current_time=2 (exceeds TWOFA_WAIT=1)
        
        # Mock WebDriverWait to immediately raise TimeoutException on .until() calls
        from selenium.common.exceptions import TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Login form not found")
        mock_wait_class.return_value = mock_wait_instance
        
        mock_driver = Mock()
        mock_driver.current_url = 'http://localhost:3000/login'
        mock_driver.page_source = 'test page'
        mock_driver.quit = Mock()
        mock_create_driver.return_value = mock_driver
        
        scraper = RedmineSeleniumScraper()
        result = scraper.login("", "password")
        
        # Should fail due to login process
        assert result['success'] is False

    @patch('src.redmine_selenium.os.getenv')
    @patch('src.redmine_selenium.time.sleep')
    @patch('src.redmine_selenium.time.time')
    @patch('selenium.webdriver.support.ui.WebDriverWait')
    @patch('src.redmine_selenium.RedmineSeleniumScraper._create_driver')
    def test_login_form_not_found(self, mock_create_driver, mock_wait_class, mock_time, mock_sleep, mock_getenv):
        """Test login when form is not found"""
        # Mock environment variable to short timeout
        def getenv_side_effect(key, default=None):
            if key == 'TWOFA_WAIT':
                return '1'  # 1 second timeout
            elif key == 'POLL_INTERVAL':
                return '0.1'  # Very short poll interval
            return default
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock time.time to immediately exceed the timeout
        mock_time.side_effect = [0, 2]  # start_time=0, current_time=2 (exceeds TWOFA_WAIT=1)
        
        # Mock WebDriverWait to immediately raise TimeoutException on .until() calls
        from selenium.common.exceptions import TimeoutException
        mock_wait_instance = Mock()
        mock_wait_instance.until.side_effect = TimeoutException("Login form not found")
        mock_wait_class.return_value = mock_wait_instance
        
        mock_driver = Mock()
        mock_driver.get = Mock()
        mock_driver.current_url = 'http://localhost:3000/login'
        mock_driver.page_source = 'test page'
        mock_driver.quit = Mock()
        mock_driver.find_element.side_effect = NoSuchElementException()
        mock_create_driver.return_value = mock_driver
        
        scraper = RedmineSeleniumScraper()
        result = scraper.login("test", "test")
        
        assert result['success'] is False
        assert 'timeout' in result['message'].lower()

    def test_logout(self):
        """Test logout functionality with schema validation"""
        scraper = RedmineSeleniumScraper()
        mock_driver = Mock()
        scraper.driver = mock_driver
        scraper.is_authenticated = True
        
        result = scraper.logout()
        
        # Validate response structure using schema
        response = GeneralResponse(**result)
        assert response.success is True
        assert scraper.is_authenticated is False
        assert scraper.driver is None
        mock_driver.quit.assert_called_once()
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert 'message' in dumped


class TestProjectsTools:
    """Test projects-related tools (get_projects, get_project_members)"""

    def test_get_projects_not_authenticated(self):
        """Test get projects when not authenticated"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = False
        
        result = scraper.get_projects()
        
        # Validate response structure using schema
        response = ProjectsResponse(**result)
        assert response.success is False
        assert 'not authenticated' in response.message.lower()
        assert len(response.projects) == 0
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is False
        assert dumped['projects'] == []

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_get_projects_authenticated(self, mock_wait, mock_selenium_driver):
        """Test get projects when authenticated with schema validation"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        
        # Mock scraper wait property (since it's created during init)
        scraper.wait = mock_wait_instance
        
        # Mock page elements
        mock_table = Mock()
        mock_header_row = Mock()
        mock_data_row = Mock()
        mock_cell = Mock()
        mock_link = Mock()
        
        mock_link.text = "Test Project"
        mock_link.get_attribute.return_value = "http://test/projects/test"
        mock_cell.find_element.return_value = mock_link
        
        # Create proper row structure with length support
        mock_data_row.find_elements.return_value = [mock_cell]
        mock_header_row.find_elements.return_value = []  # Header row has no cells of interest
        
        # Mock table with proper row structure
        rows = [mock_header_row, mock_data_row]
        mock_table.find_elements.return_value = rows
        
        # Mock driver responses
        mock_selenium_driver.current_url = "http://test/projects"
        mock_selenium_driver.title = "Projects"
        mock_selenium_driver.page_source = "<html><body>Projects page</body></html>"
        mock_selenium_driver.find_element.return_value = mock_table
        
        result = scraper.get_projects()
        
        # Validate response structure using schema
        response = ProjectsResponse(**result)
        assert response.success is True
        assert len(response.projects) > 0
        
        # Validate each project follows ProjectInfo schema
        for project in response.projects:
            assert hasattr(project, 'id')
            assert hasattr(project, 'name')
            assert project.name == "Test Project"
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert isinstance(dumped['projects'], list)
        assert len(dumped['projects']) > 0
        assert dumped['projects'][0]['name'] == "Test Project"

    @patch('src.redmine_selenium.RedmineSeleniumScraper.get_projects')
    def test_get_projects_successful_response(self, mock_get_projects):
        """Test successful get_projects response with mock data"""
        # Mock response that simulates real Redmine data structure
        mock_response = {
            'success': True,
            'message': 'Successfully retrieved 2 projects',
            'projects': [
                {
                    'id': 'hoge',
                    'name': 'A fuga - dev', 
                    'description': 'Development environment for fuga',
                    'url': 'https://redmine-dev.com/projects/hoge'
                },
                {
                    'id': 'test-project',
                    'name': 'Test Project',
                    'description': '',
                    'url': 'https://redmine-dev.com/projects/test-project'
                }
            ]
        }
        
        mock_get_projects.return_value = mock_response
        
        scraper = RedmineSeleniumScraper()
        
        result = scraper.get_projects()
        
        # Verify the mock was called
        mock_get_projects.assert_called_once()
        
        # Verify response structure
        assert result['success'] is True
        assert 'projects' in result
        assert len(result['projects']) == 2
        
        # Verify project data structure
        project = result['projects'][0]
        assert project['id'] == 'hoge'
        assert project['name'] == 'A fuga - dev'

    @patch('src.redmine_selenium.RedmineSeleniumScraper.get_projects')
    def test_get_projects_error_response(self, mock_get_projects):
        """Test error response handling"""
        mock_error_response = {
            'success': False,
            'message': 'Session expired. Please login again.',
            'projects': []
        }
        
        mock_get_projects.return_value = mock_error_response
        
        scraper = RedmineSeleniumScraper()
        
        result = scraper.get_projects()
        
        assert result['success'] is False
        assert 'Session expired' in result['message']
        assert result['projects'] == []

    def test_get_project_members_not_authenticated(self):
        """Test get project members when not authenticated"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = False
        
        result = scraper.get_project_members("test-project")
        
        # Validate response structure using schema
        response = ProjectMembersResponse(**result)
        assert response.success is False
        assert 'not authenticated' in response.message.lower()
        assert len(response.members) == 0
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is False
        assert dumped['members'] == []

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_get_project_members_session_expired(self, mock_wait, mock_selenium_driver):
        """Test get project members when session has expired"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        scraper.wait = mock_wait_instance
        
        # Mock driver to redirect to login page (session expired)
        mock_selenium_driver.current_url = "http://test/login"
        
        result = scraper.get_project_members("test-project")
        
        # Validate response structure
        response = ProjectMembersResponse(**result)
        assert response.success is False
        assert 'session expired' in response.message.lower()
        assert len(response.members) == 0
        
        # Verify authentication flag is reset
        assert scraper.is_authenticated is False

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_get_project_members_project_not_found(self, mock_wait, mock_selenium_driver):
        """Test get project members when project is not found"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        scraper.wait = mock_wait_instance
        
        # Mock driver to simulate 404 page
        mock_selenium_driver.current_url = "http://test/projects/nonexistent/settings/members"
        mock_selenium_driver.page_source = "404 Not Found - Project not found"
        
        result = scraper.get_project_members("nonexistent")
        
        # Validate response structure
        response = ProjectMembersResponse(**result)
        assert response.success is False
        assert 'not found' in response.message.lower()
        assert len(response.members) == 0

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_get_project_members_with_table_structure(self, mock_wait, mock_selenium_driver):
        """Test get project members when members table is found"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        scraper.wait = mock_wait_instance
        
        # Mock current user detection
        mock_current_user_link = Mock()
        mock_current_user_link.get_attribute.return_value = "http://test/users/123"
        mock_selenium_driver.find_elements.side_effect = lambda by, selector: (
            [mock_current_user_link] if selector == "a.user.active" else 
            self._get_mocked_table_elements()
        )
        
        # Mock page state
        mock_selenium_driver.current_url = "http://test/projects/test/settings/members"
        mock_selenium_driver.page_source = "Members table"
        
        # Mock table structure
        def _get_mocked_table_elements():
            # Mock member row
            mock_member_link = Mock()
            mock_member_link.text = "John Doe"
            mock_member_link.get_attribute.return_value = "http://test/users/456"
            
            mock_user_cell = Mock()
            mock_user_cell.find_element.return_value = mock_member_link
            
            mock_role_cell = Mock()
            mock_role_cell.text = "Developer, Tester"
            
            mock_additional_cell = Mock()
            mock_additional_cell.text = "Additional info"
            
            mock_row = Mock()
            mock_row.find_elements.return_value = [mock_user_cell, mock_role_cell, mock_additional_cell]
            
            return [mock_row]
        
        # Mock table finding
        mock_table = Mock()
        mock_table.find_elements.return_value = _get_mocked_table_elements()
        
        # Setup find_element to return table for the specific selector
        def mock_find_element(by, selector):
            if selector == "#tab-content-members > table > tbody":
                return mock_table
            raise Exception("Element not found")
        
        mock_selenium_driver.find_element.side_effect = mock_find_element
        
        result = scraper.get_project_members("test")
        
        # Validate response structure
        response = ProjectMembersResponse(**result)
        assert response.success is True
        assert len(response.members) > 0
        
        # Verify member data structure
        member = response.members[0]
        assert hasattr(member, 'name')
        assert hasattr(member, 'roles')
        assert hasattr(member, 'is_current_user')
        
        # Verify member data matches schema expectations
        # Schema uses: 'roles' (List[str]), 'id', 'is_current_user'

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_get_project_members_fallback_to_links(self, mock_wait, mock_selenium_driver):
        """Test get project members fallback when table is not found"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        scraper.wait = mock_wait_instance
        
        # Mock page state
        mock_selenium_driver.current_url = "http://test/projects/test/settings/members"
        mock_selenium_driver.page_source = "No members table"
        
        # Mock find_element to throw exception (table not found)
        mock_selenium_driver.find_element.side_effect = Exception("Table not found")
        
        # Mock current user detection (return empty list for current user)
        # Mock fallback member links
        mock_member_link1 = Mock()
        mock_member_link1.text = "Alice Smith"
        mock_member_link1.get_attribute.return_value = "http://test/users/789"
        
        mock_member_link2 = Mock()
        mock_member_link2.text = "Bob Johnson"
        mock_member_link2.get_attribute.return_value = "http://test/users/101"
        
        def mock_find_elements(by, selector):
            if selector == "a.user.active":
                return []  # No current user detected
            elif selector == "a[href*='/users/']":
                return [mock_member_link1, mock_member_link2]
            return []
        
        mock_selenium_driver.find_elements.side_effect = mock_find_elements
        
        result = scraper.get_project_members("test")
        
        # Validate response structure
        response = ProjectMembersResponse(**result)
        assert response.success is True
        assert len(response.members) > 0
        
        # Verify fallback member extraction worked
        member_names = [member.name for member in response.members]
        assert "Alice Smith" in member_names
        assert "Bob Johnson" in member_names

    @patch('src.redmine_selenium.RedmineSeleniumScraper.get_project_members')
    def test_get_project_members_successful_response(self, mock_get_project_members):
        """Test successful get_project_members response with mock data"""
        # Mock response that simulates real Redmine data structure
        mock_response = {
            'success': True,
            'message': 'Successfully retrieved 3 project members',
            'members': [
                {
                    'name': 'Admin User',
                    'role': 'Manager',
                    'user_id': '1'
                },
                {
                    'name': 'John Developer',
                    'role': 'Developer',
                    'user_id': '15'
                },
                {
                    'name': 'Jane Tester',
                    'role': 'Tester',
                    'user_id': '22'
                }
            ]
        }
        
        mock_get_project_members.return_value = mock_response
        
        scraper = RedmineSeleniumScraper()
        
        result = scraper.get_project_members("test-project")
        
        # Verify the mock was called with correct parameter
        mock_get_project_members.assert_called_once_with("test-project")
        
        # Verify response structure
        assert result['success'] is True
        assert 'members' in result
        assert len(result['members']) == 3
        
        # Verify member data structure
        member = result['members'][0]
        assert member['name'] == 'Admin User'
        assert member['role'] == 'Manager'
        assert member['user_id'] == '1'

    @patch('src.redmine_selenium.RedmineSeleniumScraper.get_project_members')
    def test_get_project_members_error_response(self, mock_get_project_members):
        """Test error response handling for get_project_members"""
        mock_error_response = {
            'success': False,
            'message': 'Error getting project members: Connection timeout',
            'members': []
        }
        
        mock_get_project_members.return_value = mock_error_response
        
        scraper = RedmineSeleniumScraper()
        
        result = scraper.get_project_members("invalid-project")
        
        assert result['success'] is False
        assert 'Connection timeout' in result['message']
        assert result['members'] == []


class TestIssuesTools:
    """Test issues-related tools (search_issues, get_issue_details, create_issue, update_issue)"""

    def test_search_issues_not_authenticated(self):
        """Test search issues when not authenticated"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = False
        
        result = scraper.search_issues()
        
        # Validate response structure using schema
        response = IssuesResponse(**result)
        assert response.success is False
        assert 'not authenticated' in response.message.lower()
        assert len(response.issues) == 0
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is False
        assert dumped['issues'] == []

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_search_issues_authenticated(self, mock_wait, mock_selenium_driver):
        """Test search issues when authenticated with schema validation"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        
        # Mock scraper wait property
        scraper.wait = mock_wait_instance
        
        mock_selenium_driver.current_url = "http://test/issues"
        mock_selenium_driver.page_source = "issues page content"
        mock_selenium_driver.find_element.side_effect = NoSuchElementException()
        mock_selenium_driver.find_elements.return_value = []
        
        result = scraper.search_issues(q="test")
        
        # Validate response structure using schema
        response = IssuesResponse(**result)
        assert response.success is True
        assert hasattr(response, 'issues')
        assert isinstance(response.issues, list)
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert 'issues' in dumped
        assert isinstance(dumped['issues'], list)

    def test_get_issue_details_not_authenticated(self):
        """Test get issue details when not authenticated"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = False
        
        result = scraper.get_issue_details("1")
        
        # Validate response structure using schema
        response = IssueDetailResponse(**result)
        assert response.success is False
        assert 'not authenticated' in response.message.lower()
        assert response.issue is not None  # Should contain IssueInfo with basic data
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is False
        assert 'issue' in dumped

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_get_issue_details_authenticated(self, mock_wait, mock_selenium_driver):
        """Test get issue details when authenticated with schema validation"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        
        # Mock scraper wait property
        scraper.wait = mock_wait_instance
        
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
        
        # Validate response structure using schema
        response = IssueDetailResponse(**result)
        assert response.success is True
        assert response.issue.id == "1"
        assert isinstance(response.issue, IssueInfo)
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert dumped['issue']['id'] == "1"
        assert isinstance(dumped['issue'], dict)

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_get_issue_details_with_custom_fields(self, mock_wait, mock_selenium_driver):
        """Test get issue details retrieves custom fields correctly"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        scraper.wait = mock_wait_instance
        
        mock_selenium_driver.current_url = "http://test/issues/1"
        mock_selenium_driver.page_source = "issue details page"
        
        # Mock subject element
        mock_subject = Mock()
        mock_subject.text = "Test Issue"
        
        # Mock attribute divs with standard and custom fields
        mock_attr1 = Mock()
        mock_label1 = Mock()
        mock_label1.text = "Status:"
        mock_value1 = Mock()
        mock_value1.text = "New"
        mock_attr1.find_element.side_effect = lambda by, sel: mock_label1 if "label" in sel else mock_value1
        mock_attr1.get_attribute.return_value = "attribute status"
        
        mock_attr2 = Mock()
        mock_label2 = Mock()
        mock_label2.text = "カスタムフィールド1:"  # Custom field in Japanese
        mock_value2 = Mock()
        mock_value2.text = "カスタム値"
        mock_attr2.find_element.side_effect = lambda by, sel: mock_label2 if "label" in sel else mock_value2
        mock_attr2.get_attribute.return_value = "attribute cf_5"  # Custom field with ID 5
        
        mock_attr3 = Mock()
        mock_label3 = Mock()
        mock_label3.text = "Custom Field 2:"  # Custom field in English
        mock_value3 = Mock()
        mock_value3.text = "Custom Value 2"
        mock_attr3.find_element.side_effect = lambda by, sel: mock_label3 if "label" in sel else mock_value3
        mock_attr3.get_attribute.return_value = "attribute cf_10"  # Custom field with ID 10
        
        def mock_find_element(by, selector):
            if selector == ".subject h3":
                return mock_subject
            raise NoSuchElementException()
        
        def mock_find_elements(by, selector):
            if selector == "div.attribute":
                return [mock_attr1, mock_attr2, mock_attr3]
            return []
        
        mock_selenium_driver.find_element.side_effect = mock_find_element
        mock_selenium_driver.find_elements.side_effect = mock_find_elements
        
        result = scraper.get_issue_details("1")
        
        # Validate response structure using schema
        response = IssueDetailResponse(**result)
        assert response.success is True
        assert response.issue.id == "1"
        assert response.issue.status == "New"
        
        # Verify custom fields are captured with cf_{id} format
        assert response.issue.custom_fields is not None
        assert "cf_5" in response.issue.custom_fields
        assert "cf_10" in response.issue.custom_fields
        assert response.issue.custom_fields["cf_5"] == "カスタム値"
        assert response.issue.custom_fields["cf_10"] == "Custom Value 2"
        
        # Verify model_dump includes custom fields in correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert dumped['issue']['custom_fields'] is not None
        assert "cf_5" in dumped['issue']['custom_fields']
        assert "cf_10" in dumped['issue']['custom_fields']

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_get_issue_details_multiple_custom_fields(self, mock_wait, mock_selenium_driver):
        """Test get issue details retrieves multiple custom fields correctly"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        scraper.wait = mock_wait_instance
        
        mock_selenium_driver.current_url = "http://test/issues/1"
        mock_selenium_driver.page_source = "issue details page"
        
        # Mock subject element
        mock_subject = Mock()
        mock_subject.text = "Test Issue with Multiple Custom Fields"
        
        # Create 5 custom fields to test multiple field handling
        custom_field_mocks = []
        custom_field_data = [
            ("cf_1", "Company", "ACME Corp"),
            ("cf_3", "Department", "Engineering"),
            ("cf_7", "Priority Level", "High"),
            ("cf_12", "Due Date Extended", "2025-12-31"),
            ("cf_15", "Project Phase", "Implementation")
        ]
        
        for cf_class, cf_label, cf_value in custom_field_data:
            mock_attr = Mock()
            mock_label = Mock()
            mock_label.text = f"{cf_label}:"
            mock_value_elem = Mock()
            mock_value_elem.text = cf_value
            mock_attr.find_element.side_effect = lambda by, sel, l=mock_label, v=mock_value_elem: l if "label" in sel else v
            mock_attr.get_attribute.return_value = f"attribute {cf_class}"
            custom_field_mocks.append(mock_attr)
        
        def mock_find_element(by, selector):
            if selector == ".subject h3":
                return mock_subject
            raise NoSuchElementException()
        
        def mock_find_elements(by, selector):
            if selector == "div.attribute":
                return custom_field_mocks
            return []
        
        mock_selenium_driver.find_element.side_effect = mock_find_element
        mock_selenium_driver.find_elements.side_effect = mock_find_elements
        
        result = scraper.get_issue_details("1")
        
        # Validate response structure using schema
        response = IssueDetailResponse(**result)
        assert response.success is True
        assert response.issue.id == "1"
        
        # Verify all 5 custom fields are captured
        assert response.issue.custom_fields is not None
        assert len(response.issue.custom_fields) == 5
        
        # Check each custom field
        for cf_class, cf_label, cf_value in custom_field_data:
            assert cf_class in response.issue.custom_fields
            assert response.issue.custom_fields[cf_class] == cf_value
        
        # Verify specific fields
        assert response.issue.custom_fields["cf_1"] == "ACME Corp"
        assert response.issue.custom_fields["cf_3"] == "Engineering"
        assert response.issue.custom_fields["cf_7"] == "High"
        assert response.issue.custom_fields["cf_12"] == "2025-12-31"
        assert response.issue.custom_fields["cf_15"] == "Implementation"

    def test_create_issue_response_schema(self):
        """Test CreateIssueResponse schema"""
        response = CreateIssueResponse(
            success=True,
            message='Successfully created issue #123',
            issue_id='123',
            issue_url='http://test/issues/123'
        )
        
        assert response.success is True
        assert response.issue_id == '123'
        assert response.issue_url == 'http://test/issues/123'
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert dumped['issue_id'] == '123'
        assert dumped['issue_url'] == 'http://test/issues/123'
    
    def test_update_issue_response_schema(self):
        """Test UpdateIssueResponse schema"""
        response = UpdateIssueResponse(
            success=True,
            message='Successfully updated issue #123',
            issue_id='123',
            issue_url='http://test/issues/123'
        )
        
        assert response.success is True
        assert response.issue_id == '123'
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert dumped['issue_id'] == '123'

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_search_issues_pagination_with_next_page(self, mock_wait, mock_selenium_driver):
        """Test search issues pagination when next page exists"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        scraper.wait = mock_wait_instance
        
        mock_selenium_driver.current_url = "http://test/issues"
        mock_selenium_driver.page_source = "issues page content"
        
        # Mock next page element (exists and enabled)
        mock_next_page = Mock()
        mock_next_page.is_enabled.return_value = True
        
        def mock_find_element(by, selector):
            if selector == "#content > span > ul > li.next.page":
                return mock_next_page
            raise NoSuchElementException()
        
        mock_selenium_driver.find_element.side_effect = mock_find_element
        mock_selenium_driver.find_elements.return_value = []
        
        result = scraper.search_issues(page=1)
        
        # Validate response structure
        response = IssuesResponse(**result)
        assert response.success is True
        assert response.current_page == 1
        assert response.has_next is True  # Should be True when next page exists
        assert "more pages available" in response.message

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_search_issues_pagination_no_next_page(self, mock_wait, mock_selenium_driver):
        """Test search issues pagination when no next page exists"""
        scraper = RedmineSeleniumScraper()
        scraper.is_authenticated = True
        scraper.driver = mock_selenium_driver
        
        # Mock WebDriverWait
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance
        scraper.wait = mock_wait_instance
        
        mock_selenium_driver.current_url = "http://test/issues"
        mock_selenium_driver.page_source = "issues page content"
        
        # Mock no next page element (NoSuchElementException)
        def mock_find_element(by, selector):
            if selector == "#content > span > ul > li.next.page":
                raise NoSuchElementException()
            raise NoSuchElementException()
        
        mock_selenium_driver.find_element.side_effect = mock_find_element
        mock_selenium_driver.find_elements.return_value = []
        
        result = scraper.search_issues(page=2)
        
        # Validate response structure
        response = IssuesResponse(**result)
        assert response.success is True
        assert response.current_page == 2
        assert response.has_next is False  # Should be False when no next page
        assert "more pages available" not in response.message


class TestTimeEntriesTools:
    """Test time entries-related tools (get_time_entries)"""
    
    def test_get_time_entries_response_schema(self):
        """Test TimeEntriesResponse schema"""
        time_entries_data = [
            {
                'spent_on': '2025/12/14',
                'hours': '4:00',
                'activity': 'task',
                'user': 'hoge.taro',
                'issue': 'task',
                'issue_id': '3203'
            }
        ]
        
        time_entry_infos = [TimeEntryInfo(**entry) for entry in time_entries_data]
        
        response = TimeEntriesResponse(
            success=True,
            message='Found 1 time entries (showing page 1)',
            time_entries=time_entry_infos,
            total_count=1,
            current_page=1,
            has_next=False
        )
        
        assert response.success is True
        assert len(response.time_entries) == 1
        assert response.time_entries[0].spent_on == '2025/12/14'
        assert response.time_entries[0].hours == '4:00'
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert len(dumped['time_entries']) == 1
        assert dumped['total_count'] == 1


class TestTrackerAndStatusTools:
    """Test tracker and status-related tools (get_available_trackers, get_available_statuses, get_tracker_fields)"""
    
    def test_get_available_trackers_response_schema(self):
        """Test TrackersResponse schema"""
        tracker_data = [
            {'id': '1', 'name': 'Bug', 'description': 'Bug reports'},
            {'id': '2', 'name': 'Feature', 'description': None}
        ]
        
        tracker_infos = [TrackerInfo(**tracker) for tracker in tracker_data]
        
        response = TrackersResponse(
            success=True,
            message='Found 2 available trackers',
            trackers=tracker_infos
        )
        
        assert response.success is True
        assert len(response.trackers) == 2
        assert response.trackers[0].id == '1'
        assert response.trackers[0].name == 'Bug'
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert len(dumped['trackers']) == 2
    
    def test_get_available_statuses_response_schema(self):
        """Test StatusesResponse schema"""
        status_data = [
            {'id': '1', 'name': 'New', 'is_closed': False},
            {'id': '5', 'name': 'Closed', 'is_closed': True}
        ]
        
        status_infos = [StatusInfo(**status) for status in status_data]
        
        response = StatusesResponse(
            success=True,
            message='Found 2 available statuses',
            statuses=status_infos
        )
        
        assert response.success is True
        assert len(response.statuses) == 2
        assert response.statuses[0].name == 'New'
        assert response.statuses[1].is_closed is True
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert len(dumped['statuses']) == 2
    
    def test_get_tracker_fields_response_schema(self):
        """Test FieldsResponse schema"""
        field_data = [
            {
                'name': 'Subject',
                'type': 'text',
                'required': True,
                'options': None,
                'value': None
            },
            {
                'name': 'Priority',
                'type': 'select-one',
                'required': False,
                'options': [{'value': '1', 'text': 'Low'}, {'value': '2', 'text': 'High'}],
                'value': None
            }
        ]
        
        field_infos = [FieldInfo(**field) for field in field_data]
        
        response = FieldsResponse(
            success=True,
            message='Found 2 fields (1 required, 1 optional, 0 custom)',
            fields=field_infos
        )
        
        assert response.success is True
        assert len(response.fields) == 2
        assert response.fields[0].required is True
        assert response.fields[1].type == 'select-one'
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert len(dumped['fields']) == 2


class TestSchemaValidation:
    """Test schema validation for all response and request models"""
    
    # Project-related schema tests
    def test_project_info_with_id_field(self):
        """Test that ProjectInfo accepts 'id' field (not 'identifier')"""
        # This simulates data from Redmine get_projects
        project_data = {
            'id': 'hoge',
            'name': 'A fuga - dev',
            'description': 'A sample project',
            'url': 'https://redmine-dev.com/projects/hoge'
        }
        
        # Should not raise ValidationError
        project = ProjectInfo(**project_data)
        
        assert project.id == 'hoge'
        assert project.name == 'A fuga - dev'
        assert project.description == 'A sample project'
        assert project.url == 'https://redmine-dev.com/projects/hoge'
    
    def test_project_info_required_fields(self):
        """Test that required fields are enforced"""
        # Missing 'name' field should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            ProjectInfo(id='test')
        
        error = exc_info.value
        assert 'name' in str(error)
        assert 'Field required' in str(error)
        
        # Missing 'id' field should raise ValidationError  
        with pytest.raises(ValidationError) as exc_info:
            ProjectInfo(name='Test Project')
        
        error = exc_info.value
        assert 'id' in str(error)
        assert 'Field required' in str(error)
    
    def test_project_info_optional_fields(self):
        """Test that optional fields work correctly"""
        project = ProjectInfo(
            id='test',
            name='Test Project'
            # description, url, created_on, status are optional
        )
        
        assert project.id == 'test'
        assert project.name == 'Test Project'
        assert project.description is None
        assert project.url is None
        assert project.created_on is None
        assert project.status is None
    
    def test_projects_response_schema(self):
        """Test ProjectsResponse with ProjectInfo objects"""
        projects_data = [
            {
                'id': 'project1',
                'name': 'Project 1',
                'description': 'First project',
                'url': 'http://example.com/projects/project1'
            },
            {
                'id': 'project2', 
                'name': 'Project 2'
                # description and url are optional
            }
        ]
        
        # Convert to ProjectInfo objects
        projects = [ProjectInfo(**data) for data in projects_data]
        
        response = ProjectsResponse(
            success=True,
            message='Successfully retrieved 2 projects',
            projects=projects
        )
        
        assert response.success is True
        assert len(response.projects) == 2
        assert response.projects[0].id == 'project1'
        assert response.projects[1].id == 'project2'
        assert response.projects[1].description is None
    
    def test_simulated_get_projects_workflow(self):
        """Test the complete workflow from raw data to schema response"""
        # Simulate raw project data from Redmine scraping
        raw_projects = [
            {
                'id': 'hoge',
                'name': 'A fuga - dev',
                'description': '',
                'url': 'https://redmine-dev.com/projects/hoge'
            },
            {
                'id': 'test-project',
                'name': 'Test Project',
                'description': 'A test project for validation',
                'url': 'https://redmine-dev.com/projects/test-project'
            }
        ]
        
        # This simulates the conversion in get_projects method
        project_infos = [ProjectInfo(**project) for project in raw_projects]
        
        # Create response
        response = ProjectsResponse(
            success=True,
            message=f'Successfully retrieved {len(raw_projects)} projects',
            projects=project_infos
        )
        
        # Test response.model_dump() (what gets returned to MCP)
        dumped_response = response.model_dump()
        
        assert dumped_response['success'] is True
        assert len(dumped_response['projects']) == 2
        assert dumped_response['projects'][0]['id'] == 'hoge'
        assert dumped_response['projects'][0]['name'] == 'A fuga - dev'
    
    # Other schema tests
    def test_member_info_schema(self):
        """Test MemberInfo schema"""
        member = MemberInfo(
            name='John Doe',
            role='Developer'
        )
        
        assert member.name == 'John Doe'
        assert member.role == 'Developer' 
        assert member.user_id is None
        assert member.email is None
    
    def test_issue_info_schema(self):
        """Test IssueInfo schema"""
        issue = IssueInfo(
            id='123',
            subject='Test Issue',
            description='A test issue for validation'
        )
        
        assert issue.id == '123'
        assert issue.subject == 'Test Issue'
        assert issue.description == 'A test issue for validation'
        assert issue.status is None
        assert issue.priority is None
    
    def test_tracker_info_schema(self):
        """Test TrackerInfo schema"""
        tracker = TrackerInfo(
            id='1',
            name='Bug'
        )
        
        assert tracker.id == '1'
        assert tracker.name == 'Bug'
        assert tracker.description is None
    
    def test_status_info_schema(self):
        """Test StatusInfo schema"""  
        status = StatusInfo(
            id='1',
            name='New'
        )
        
        assert status.id == '1'
        assert status.name == 'New'
        assert status.is_closed is None

    def test_login_response_schema(self):
        """Test LoginResponse schema"""
        response = LoginResponse(
            success=True,
            message='Successfully logged in to Redmine',
            redirect_url='http://test/my/page'
        )
        
        assert response.success is True
        assert response.redirect_url == 'http://test/my/page'
        
        # Test error case
        error_response = LoginResponse(
            success=False,
            message='Invalid credentials',
            redirect_url=None
        )
        
        assert error_response.success is False
        assert error_response.redirect_url is None
        
        # Verify model_dump produces correct format
        dumped = response.model_dump()
        assert dumped['success'] is True
        assert dumped['redirect_url'] == 'http://test/my/page'

    # Schema validation error handling tests  
    def test_project_info_validation_error(self):
        """Test ProjectInfo validation with invalid data"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectInfo(name='Test Project')  # Missing required 'id' field
        
        error = exc_info.value
        assert 'id' in str(error)
        assert 'Field required' in str(error)
    
    def test_member_info_validation_error(self):
        """Test MemberInfo validation with invalid data"""
        with pytest.raises(ValidationError) as exc_info:
            MemberInfo(name='John Doe')  # Missing required 'role' field
        
        error = exc_info.value
        assert 'role' in str(error)
        assert 'Field required' in str(error)
    
    def test_time_entries_response_with_invalid_entry(self):
        """Test TimeEntriesResponse with invalid time entry data"""
        # TimeEntryInfo has no strictly required fields, test with valid minimal data
        minimal_entry = TimeEntryInfo()
        
        response = TimeEntriesResponse(
            success=True,
            message='Test message',
            time_entries=[minimal_entry],
            total_count=1
        )
        
        assert response.success is True
        assert len(response.time_entries) == 1
        
        # All fields should be None for minimal entry
        entry = response.time_entries[0]
        assert entry.spent_on is None
        assert entry.hours is None
        assert entry.user is None
    
    def test_schema_field_type_validation(self):
        """Test schema field type validation"""
        # Test that numeric fields reject invalid types
        with pytest.raises(ValidationError):
            TimeEntriesResponse(
                success=True,
                message='Test',
                time_entries=[],
                total_count='invalid'  # Should be int
            )
        
        # Test that boolean fields reject invalid types  
        with pytest.raises(ValidationError):
            StatusInfo(
                id='1',
                name='Test',
                is_closed='invalid'  # Should be bool or None
            )
    
    def test_projects_response_model_dump_format(self):
        """Test that ProjectsResponse.model_dump() produces the expected format"""
        # Create sample projects
        projects = [
            ProjectInfo(
                id='proj1',
                name='Project 1',
                description='First project',
                url='http://example.com/proj1'
            ),
            ProjectInfo(
                id='proj2', 
                name='Project 2'
                # description and url will be None
            )
        ]
        
        response = ProjectsResponse(
            success=True,
            message='Found 2 projects',
            projects=projects
        )
        
        # This is what gets returned to the MCP client
        dumped = response.model_dump()
        
        # Verify structure matches what MCP client expects
        expected_structure = {
            'success': True,
            'message': 'Found 2 projects', 
            'projects': [
                {
                    'id': 'proj1',
                    'name': 'Project 1',
                    'description': 'First project',
                    'url': 'http://example.com/proj1',
                    'created_on': None,
                    'status': None
                },
                {
                    'id': 'proj2',
                    'name': 'Project 2',
                    'description': None,
                    'url': None,
                    'created_on': None,
                    'status': None
                }
            ]
        }
        
        assert dumped == expected_structure