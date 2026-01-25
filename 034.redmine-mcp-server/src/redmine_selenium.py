"""
Redmine Selenium Scraper
Handles authentication and data extraction from Redmine using Selenium WebDriver
"""

import time
import logging
import os
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Import schemas for response validation
try:
    from schemas import (
        LoginResponse, ProjectsResponse, ProjectMembersResponse, IssuesResponse,
        IssueDetailResponse, TrackersResponse, StatusesResponse, FieldsResponse,
        TimeEntriesResponse, CreateIssueResponse, UpdateIssueResponse,
        ServerInfoResponse, GeneralResponse, ProjectInfo, MemberInfo, IssueInfo,
        TrackerInfo, StatusInfo, FieldInfo, TimeEntryInfo, ServerInfo
    )
except ImportError:
    # If running standalone, define minimal classes
    class LoginResponse:
        pass
    class ProjectsResponse:
        pass
    # Add other minimal classes as needed...

# Load environment variables
load_dotenv()

# Import config
try:
    from config import config
except ImportError:
    try:
        from .config import config
    except ImportError:
        # Fallback config
        class MinimalConfig:
            def __init__(self):
                self.base_url = os.getenv('REDMINE_URL', 'http://localhost:3000')
                if self.base_url.endswith('/'):
                    self.base_url = self.base_url[:-1]
                self.login_url = f"{self.base_url}/login"
                self.logout_url = f"{self.base_url}/logout"
                self.projects_url = f"{self.base_url}/projects"
                self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        config = MinimalConfig()

# Set up logging
logging.basicConfig(level=logging.INFO if config.debug else logging.WARNING)
logger = logging.getLogger(__name__)

class RedmineSeleniumError(Exception):
    """Custom exception for Redmine Selenium errors"""
    pass

class RedmineSeleniumScraper:
    """Redmine web scraper using Selenium WebDriver"""
    
    def __init__(self):
        self.driver = None
        self.is_authenticated = False
        self.headless_mode = False
        self.wait_time = int(os.getenv('SELENIUM_WAIT', '60'))
        self.wait = None
        self.auto_switch_headless = os.getenv('AUTO_SWITCH_HEADLESS', 'false').lower() == 'true'
        
    def _create_driver(self, headless: bool = False) -> webdriver.Chrome:
        """Create Chrome WebDriver instance"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
        
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver-manager to automatically download and manage ChromeDriver
        #service = Service(ChromeDriverManager().install())
        #driver = webdriver.Chrome(service=service, options=chrome_options)
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _switch_to_headless(self):
        """Switch from visible browser to headless mode"""
        if self.driver and not self.headless_mode:
            logger.info("Closing visible browser and switching to headless mode")
            
            # Save current cookies and session state
            cookies = self.driver.get_cookies()
            current_url = self.driver.current_url
            
            # Close current visible browser
            self.driver.quit()
            logger.info("Visible browser closed")
            
            # Create new headless driver
            logger.info("Starting headless browser")
            self.driver = self._create_driver(headless=True)
            self.headless_mode = True
            self.wait = WebDriverWait(self.driver, self.wait_time)
            
            # Navigate to base URL first
            self.driver.get(config.base_url)
            
            # Restore cookies
            restored_cookies = 0
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                    restored_cookies += 1
                except Exception as e:
                    logger.debug(f"Could not restore cookie {cookie.get('name')}: {e}")
            
            logger.debug(f"Restored {restored_cookies} cookies")
            
            # Navigate back to current URL to apply cookies
            self.driver.get(current_url)
            
            logger.info("Successfully switched to headless mode")
    
    def _validate_project_id(self, project_id: str) -> tuple[bool, str, list]:
        """
        Validate if a project exists
        
        Args:
            project_id: Project ID to validate
            
        Returns:
            Tuple of (is_valid, error_message, available_project_ids)
        """
        logger.debug(f"Verifying project '{project_id}' exists")
        projects_result = self.get_projects()
        
        if projects_result.get('success'):
            project_ids = [p['id'] for p in projects_result.get('projects', [])]
            if project_id not in project_ids:
                error_msg = f"Project '{project_id}' not found. Available projects: {', '.join(project_ids[:5])}" + \
                          (f" (and {len(project_ids) - 5} more)" if len(project_ids) > 5 else "")
                logger.warning(error_msg)
                return False, error_msg, project_ids
            else:
                logger.debug(f"Project '{project_id}' verified to exist")
                return True, "", project_ids
        else:
            error_msg = f"Could not verify project existence: {projects_result.get('message')}"
            logger.warning(error_msg)
            return True, "", []  # Allow to proceed if verification fails
    
    def login(self) -> Dict[str, Any]:
        """
        Login to Redmine using Selenium
        
        Reads credentials from environment variables REDMINE_USERNAME and REDMINE_PASSWORD.
        If environment variables are not set, waits for user to manually input credentials.
            
        Returns:
            Dict with login status and message
        """
        try:
            logger.info(f"Starting login process to {config.login_url}")
            
            # Create visible browser for authentication
            if self.driver:
                self.driver.quit()
            
            self.driver = self._create_driver(headless=False)
            self.headless_mode = False
            self.wait = WebDriverWait(self.driver, self.wait_time)
            
            # Navigate to login page with back_url parameter for redirect after login
            from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
            parsed_url = urlparse(config.login_url)
            query_params = parse_qs(parsed_url.query)
            query_params['back_url'] = [config.projects_url]
            
            # Rebuild URL with back_url parameter
            new_query = urlencode(query_params, doseq=True)
            login_url_with_redirect = urlunparse((
                parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                parsed_url.params, new_query, parsed_url.fragment
            ))
            
            logger.info(f"Navigating to login page with redirect: {login_url_with_redirect}")
            self.driver.get(login_url_with_redirect)

            try:
                # Get credentials from environment variables
                username = os.getenv('REDMINE_USERNAME')
                password = os.getenv('REDMINE_PASSWORD')
                
                # Find username field
                username_field = self.wait.until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                
                # Find password field
                password_field = self.driver.find_element(By.ID, "password")
                
                # Fill in credentials if available from environment variables
                if username and password:
                    logger.info("Using credentials from environment variables")
                    username_field.clear()
                    username_field.send_keys(username)
                    password_field.clear()
                    password_field.send_keys(password)
                    
                    # Submit form
                    login_button = self.driver.find_element(By.ID, "login-submit")
                    login_button.click()
                    
                    logger.info("Credentials submitted, waiting for authentication to complete...")
                else:
                    logger.info("No credentials found in environment variables (REDMINE_USERNAME, REDMINE_PASSWORD)")
                    logger.info("Please enter credentials manually in the browser window")
                    print("\n" + "="*60)
                    print("MANUAL LOGIN REQUIRED")
                    print("Environment variables REDMINE_USERNAME and REDMINE_PASSWORD not found.")
                    print("Please enter your credentials manually in the browser window.")
                    print("="*60 + "\n")
                
                # Wait for authentication completion - user will handle 2FA manually
                # Redmine will redirect to projects page or dashboard after successful auth
                logger.info(f"Waiting for authentication completion (up to {self.wait_time} seconds)")
                
                # Notify user about potential 2FA requirement
                logger.info("If 2FA is required, please complete authentication manually in the browser.")
                print("\n" + "="*60)
                print("AUTHENTICATION IN PROGRESS")
                print("If two-factor authentication is required, please complete it in the browser window.")
                print("The script will automatically continue once authentication is complete.")
                print("DO NOT CLOSE THE BROWSER WINDOW")
                print("="*60 + "\n")
                
                # Wait until we reach the projects URL (indicating successful authentication)
                self.wait.until(
                    lambda d: d.current_url == config.projects_url
                )
                
                # Authentication completed - verify by checking final URL
                final_url = config.projects_url
                logger.info(f"Authentication completed, using projects URL: {final_url}")
                
                self.is_authenticated = True
                
                # Get current user ID from page header
                current_user_id = None
                try:
                    # Look for logged in user link in header
                    user_elements = self.driver.find_elements(By.CSS_SELECTOR, "a.user.active")
                    for elem in user_elements:
                        href = elem.get_attribute("href")
                        if href:
                            user_id_match = re.search(r'/users/(\d+)', href)
                            if user_id_match:
                                current_user_id = user_id_match.group(1)
                                logger.debug(f"Current user ID detected: {current_user_id}")
                                break
                except Exception as e:
                    logger.debug(f"Could not detect current user ID: {e}")
                
                # Notify user that authentication is complete
                print("\n" + "="*60)
                print("AUTHENTICATION SUCCESSFUL!")
                print("The visible browser will now close and switch to headless mode.")
                print("Processing will continue in the background...")
                print("="*60 + "\n")
                
                # Give user a moment to see the message
                # Switch to headless mode if enabled
                if self.auto_switch_headless:
                    self._switch_to_headless()
                
                response = LoginResponse(
                    success=True,
                    message='Successfully logged in to Redmine',
                    redirect_url=final_url,
                    current_user_id=current_user_id
                )
                return response.model_dump()
                
            except TimeoutException:
                logger.error("Authentication timeout or login form not found")
                response = LoginResponse(
                    success=False,
                    message='Authentication timeout. Please check credentials and try again.'
                )
                return response.model_dump()
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            response = LoginResponse(
                success=False,
                message=f"Login error: {str(e)}"
            )
            return response.model_dump()
    
    def get_projects(self) -> Dict[str, Any]:
        """
        Get list of projects from Redmine
        
        Returns:
            Dict following ProjectsResponse schema: {'success': bool, 'message': str, 'projects': List[ProjectInfo]}
        """
        if not self.is_authenticated or not self.driver:
            response = ProjectsResponse(
                success=False,
                message='Not authenticated. Please login first.',
                projects=[]
            )
            return response.model_dump()
        
        try:
            logger.info(f"Fetching projects from {config.projects_url}")
            
            # Navigate to projects page
            self.driver.get(config.projects_url)
            
            # Wait for page to load

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            wait = WebDriverWait(self.driver, 10)
            
            # Debug: Log page title and source
            logger.debug(f"Page title: {self.driver.title}")
            page_source = self.driver.page_source
            logger.debug(f"Page source length: {len(page_source)}")
            logger.debug(f"First 500 chars: {page_source[:500]}")
            
            projects = []
            
            # Check if we're redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                response = ProjectsResponse(
                    success=False,
                    message='Session expired. Please login again.',
                    projects=[]
                )
                return response.model_dump()
            
            # Method 1: Look for project table
            try:
                project_table = self.driver.find_element(By.CSS_SELECTOR, "table.projects, table.list")
                rows = project_table.find_elements(By.TAG_NAME, "tr")
                logger.debug(f"Found project table with {len(rows)} rows")
                
                for row in rows[1:]:  # Skip header row
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 1:
                        # First cell usually contains project name and link
                        try:
                            project_link = cells[0].find_element(By.TAG_NAME, "a")
                            project_name = project_link.text.strip()
                            project_url = project_link.get_attribute("href")
                            
                            # Extract project ID from URL
                            project_id = None
                            url_match = re.search(r'/projects/([^/?]+)', project_url)
                            if url_match:
                                project_id = url_match.group(1)
                            
                            # Get description if available
                            description = ''
                            if len(cells) > 1:
                                description = cells[1].text.strip()
                            
                            if project_name and project_id:
                                projects.append({
                                    'id': project_id,
                                    'name': project_name,
                                    'description': description,
                                    'url': project_url
                                })
                        except NoSuchElementException:
                            continue
                            
            except NoSuchElementException:
                logger.debug("No project table found, trying alternative methods")
            
            # Method 2: Look for project links directly
            if not projects:
                try:
                    project_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/projects/']")
                    logger.debug(f"Found {len(project_links)} links containing '/projects/'")
                    
                    for link in project_links:
                        href = link.get_attribute("href")
                        if href and re.match(r'.*/projects/[^/?]+/?$', href):
                            project_name = link.text.strip()
                            
                            # Filter out navigation links and system links
                            if (project_name and len(project_name) > 1 and
                                project_name.lower() not in ['projects', 'new project', 'settings'] and
                                not href.endswith('/projects/new')):
                                
                                # Extract project ID from URL
                                project_id = None
                                url_match = re.search(r'/projects/([^/?]+)', href)
                                if url_match:
                                    project_id = url_match.group(1)
                                
                                if project_id and project_id != 'new':
                                    projects.append({
                                        'id': project_id,
                                        'name': project_name,
                                        'description': '',
                                        'url': href
                                    })
                except Exception as e:
                    logger.debug(f"Error finding project links: {e}")
            
            # Remove duplicates
            seen_ids = set()
            unique_projects = []
            for project in projects:
                if project['id'] and project['id'] not in seen_ids:
                    seen_ids.add(project['id'])
                    unique_projects.append(project)
            
            logger.info(f"Found {len(unique_projects)} projects")
            
            if unique_projects:
                # Convert projects dict to ProjectInfo objects
                project_infos = [ProjectInfo(**project) for project in unique_projects]
                response = ProjectsResponse(
                    success=True,
                    message=f'Successfully retrieved {len(unique_projects)} projects',
                    projects=project_infos
                )
                return response.model_dump()
            else:
                response = ProjectsResponse(
                    success=False,
                    message='No projects found on the page',
                    projects=[]
                )
                return response.model_dump()
                
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            response = ProjectsResponse(
                success=False,
                message=f"Error fetching projects: {str(e)}",
                projects=[]
            )
            return response.model_dump()
    
    def get_project_members(self, project_id: str) -> Dict[str, Any]:
        """
        Get project members from project settings page
        
        Args:
            project_id: Project ID to get members for
            
        Returns:
            Dict following ProjectMembersResponse schema
        """
        if not self.is_authenticated or not self.driver:
            response = ProjectMembersResponse(
                success=False,
                message='Not authenticated. Please login first.',
                members=[]
            )
            return response.model_dump()
        
        try:
            logger.info(f"Getting project members for project: {project_id}")
            
            # Navigate to project members page
            members_url = f"{config.base_url}/projects/{project_id}/settings/members"
            self.driver.get(members_url)
            
            # Wait for page to load

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                response = ProjectMembersResponse(
                    success=False,
                    message='Session expired. Please login again.',
                    members=[]
                )
                return response.model_dump()
            
            # Check if members page is accessible
            if '404' in self.driver.page_source or 'not found' in self.driver.page_source.lower():
                response = ProjectMembersResponse(
                    success=False,
                    message=f'Project {project_id} not found or members page not accessible.',
                    members=[]
                )
                return response.model_dump()
            
            members = []
            
            # Get current user ID from page header
            current_user_id = None
            try:
                # Look for logged in user link in header
                user_elements = self.driver.find_elements(By.CSS_SELECTOR, "a.user.active")
                for elem in user_elements:
                    href = elem.get_attribute("href")
                    if href:
                        user_id_match = re.search(r'/users/(\d+)', href)
                        if user_id_match:
                            current_user_id = user_id_match.group(1)
                            logger.debug(f"Current user ID detected: {current_user_id}")
                            break
            except Exception as e:
                logger.debug(f"Could not detect current user ID: {e}")
            
            # Look for members table
            try:
                members_table = self.driver.find_element(By.CSS_SELECTOR, "#tab-content-members > table > tbody")
                
                rows = members_table.find_elements(By.TAG_NAME, "tr")
                logger.debug(f"Found {len(rows)} rows in members table")
                
                # Process all rows (tbody doesn't include header)
                for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:  # At least user and role columns
                            try:
                                member_info = {}
                                
                                # Extract user name (usually first column)
                                user_cell = cells[0]
                                user_link = user_cell.find_element(By.TAG_NAME, "a")
                                member_info['name'] = user_link.text.strip()
                                
                                # Extract user ID from link
                                user_href = user_link.get_attribute("href")
                                user_id_match = re.search(r'/users/(\d+)', user_href)
                                if user_id_match:
                                    member_info['id'] = user_id_match.group(1)
                                
                                # Check if this is the current user
                                member_info['is_current_user'] = (
                                    current_user_id and 
                                    member_info.get('id') == current_user_id
                                )
                                
                                # Extract roles (usually second column)
                                if len(cells) > 1:
                                    roles_text = cells[1].text.strip()
                                    member_info['roles'] = [role.strip() for role in roles_text.split(',') if role.strip()]
                                
                                # Extract additional info if available
                                if len(cells) > 2:
                                    member_info['additional_info'] = cells[2].text.strip()
                                
                                members.append(member_info)
                                logger.debug(f"Added member: {member_info['name']} (ID: {member_info.get('id', 'unknown')}, Current: {member_info['is_current_user']})")
                                
                            except Exception as e:
                                logger.debug(f"Error processing member row: {e}")
                                continue

                    
            except Exception as e:
                logger.debug(f"Error processing members table: {e}")
            
            # Alternative method: look for member links directly
            if not members:
                try:
                    member_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/users/']")
                    logger.debug(f"Found {len(member_links)} user links on page")
                    
                    seen_ids = set()
                    for link in member_links:
                        try:
                            href = link.get_attribute("href")
                            user_id_match = re.search(r'/users/(\d+)', href)
                            if user_id_match:
                                user_id = user_id_match.group(1)
                                if user_id not in seen_ids:
                                    seen_ids.add(user_id)
                                    
                                    user_name = link.text.strip()
                                    if user_name:  # Skip empty links
                                        members.append({
                                            'id': user_id,
                                            'name': user_name,
                                            'roles': [],
                                            'is_current_user': (
                                                current_user_id and 
                                                user_id == current_user_id
                                            )
                                        })
                                        logger.debug(f"Added member from link: {user_name} (ID: {user_id})")
                        except Exception as e:
                            logger.debug(f"Error processing member link: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error finding member links: {e}")
            
            logger.info(f"Found {len(members)} project members")
            
            member_infos = [MemberInfo(**member) for member in members]
            response = ProjectMembersResponse(
                success=True,
                message=f'Successfully retrieved {len(members)} project members',
                members=member_infos
            )
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Error getting project members: {e}")
            response = ProjectMembersResponse(
                success=False,
                message=f"Error getting project members: {str(e)}",
                members=[]
            )
            return response.model_dump()
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout from Redmine and close browser
        
        Returns:
            Dict following GeneralResponse schema: {'success': bool, 'message': str}
        """
        try:
            if self.driver:
                logger.info("Logging out and closing browser")
                
                # Try to navigate to logout URL
                try:
                    self.driver.get(config.logout_url)
                except Exception as e:
                    logger.debug(f"Error accessing logout URL: {e}")
                
                # Close browser
                self.driver.quit()
                self.driver = None
            
            self.is_authenticated = False
            self.headless_mode = False
            
            response = GeneralResponse(
                success=True,
                message='Successfully logged out from Redmine'
            )
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            # Still clean up
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            
            self.is_authenticated = False
            self.headless_mode = False
            
            response = GeneralResponse(
                success=True,
                message=f'Logged out (with warning: {str(e)})'
            )
            return response.model_dump()
    
    def search_issues(self, **kwargs) -> Dict[str, Any]:
        """
        Search for issues in Redmine
        
        Args:
            status_id: Status ID or name
            tracker_id: Tracker ID or name
            assigned_to_id: Assigned user ID or name
            parent_id: Parent issue ID
            project_id: Project ID or identifier
            subject: Subject text search
            description: Description text search
            notes: Notes text search
            q: General text search (searches across multiple fields)
            page: Page number for pagination (default: 1)
            
        Returns:
            Dict following IssuesResponse schema
        """
        if not self.is_authenticated or not self.driver:
            response = IssuesResponse(
                success=False,
                message='Not authenticated. Please login first.',
                issues=[],
                total_count=0,
                current_page=1
            )
            return response.model_dump()
        
        try:
            logger.info("Searching for issues")
            
            # Validate project_id if provided
            project_id = kwargs.get('project_id')
            if project_id:
                is_valid, error_msg, _ = self._validate_project_id(project_id)
                if not is_valid:
                    response = IssuesResponse(
                        success=False,
                        message=error_msg,
                        issues=[],
                        total_count=0,
                        current_page=1
                    )
                    return response.model_dump()
            
            # Note: Field validation is handled by _validate_fields in calling code
            
            from urllib.parse import urlencode, quote
            
            # Build search URL with Redmine filter format
            search_params = ["set_filter=1", "sort=id:desc"]
            
            # Add filter parameters in Redmine format
            if kwargs.get('status_id'):
                search_params.extend([
                    "f[]=status_id",
                    "op[status_id]==",
                    f"v[status_id][]={kwargs['status_id']}"
                ])
            
            if kwargs.get('tracker_id'):
                search_params.extend([
                    "f[]=tracker_id",
                    "op[tracker_id]==",
                    f"v[tracker_id][]={kwargs['tracker_id']}"
                ])
            
            if kwargs.get('assigned_to_id'):
                assigned_value = "me" if kwargs['assigned_to_id'].lower() == "me" else kwargs['assigned_to_id']
                search_params.extend([
                    "f[]=assigned_to_id",
                    "op[assigned_to_id]==",
                    f"v[assigned_to_id][]={assigned_value}"
                ])
            
            if kwargs.get('parent_id'):
                search_params.extend([
                    "f[]=parent_id",
                    "op[parent_id]==",
                    f"v[parent_id][]={kwargs['parent_id']}"
                ])
            
            if kwargs.get('q') or kwargs.get('subject') or kwargs.get('description') or kwargs.get('notes'):
                # Use any_searchable for general text search
                search_text = kwargs.get('q') or kwargs.get('subject') or kwargs.get('description') or kwargs.get('notes')
                search_params.extend([
                    "f[]=any_searchable",
                    "op[any_searchable]=~",
                    f"v[any_searchable][]={search_text}"
                ])
            
            # Add empty filter field
            search_params.append("f[]=")
            
            # Add column configuration
            search_params.extend([
                "c[]=tracker",
                "c[]=status", 
                "c[]=priority",
                "c[]=subject",
                "c[]=assigned_to",
                "c[]=updated_on"
            ])
            
            # Add grouping and other parameters
            search_params.extend(["group_by=", "t[]="])
            
            # Build issues URL - use project-specific URL if project_id is provided
            if kwargs.get('project_id'):
                issues_url = f"{config.base_url}/projects/{kwargs['project_id']}/issues"
            else:
                issues_url = f"{config.base_url}/issues"
            
            # URL encode the parameters
            if search_params:
                encoded_params = []
                for param in search_params:
                    if '=' in param:
                        key, value = param.split('=', 1)
                        encoded_params.append(f"{quote(key, safe='[]')}={quote(value, safe='')}") 
                    else:
                        encoded_params.append(quote(param, safe='[]'))
                issues_url += "?" + "&".join(encoded_params)
            
            logger.debug(f"Issues search URL: {issues_url}")
            logger.debug(f"Search parameters: {kwargs}")
            
            # Navigate to issues page
            self.driver.get(issues_url)
            
            # Wait for page to load

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Debug: Log page title and current URL
            logger.debug(f"Page title: {self.driver.title}")
            logger.debug(f"Current URL after navigation: {self.driver.current_url}")
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                response = IssuesResponse(
                    success=False,
                    message='Session expired. Please login again.',
                    issues=[],
                    total_count=0,
                    current_page=kwargs.get('page', 1)
                )
                return response.model_dump()
            
            issues = []
            
            # Extract total count from page
            total_count = 0
            try:
                # Look for pagination info with pattern (1-25/101)
                pagination_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".pagination, .paginator, .page-info, .items-info")
                
                for element in pagination_elements:
                    text = element.text.strip()
                    logger.debug(f"Pagination text: {text}")
                    # Look for patterns like "(1-25/101)" or "1-25/101"
                    match = re.search(r'\(?\d+-\d+/(\d+)\)?', text)
                    if match:
                        total_count = int(match.group(1))
                        logger.debug(f"Found total count from pagination: {total_count}")
                        break
                            
            except Exception as e:
                logger.debug(f"Could not extract total count: {e}")
            
            # Extract issues from table
            try:
                # Look for issues table with specific selector
                issues_table = None
                try:
                    issues_table = self.driver.find_element(By.CSS_SELECTOR, "#content table.list.issues")
                    logger.debug("Found issues table with selector: #content table.list.issues")
                except Exception as e:
                    logger.debug(f"Issues table selector failed: {e}")
                    issues_table = None
                
                if issues_table:
                    rows = issues_table.find_elements(By.TAG_NAME, "tr")
                    logger.debug(f"Found {len(rows)} rows in issues table")
                    
                    # Skip header row(s) - look for rows with td elements
                    data_rows = []
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if cells:  # Has td elements, likely a data row
                            data_rows.append(row)
                    
                    logger.debug(f"Found {len(data_rows)} data rows")
                    
                    for row_idx, row in enumerate(data_rows):
                        cells = row.find_elements(By.TAG_NAME, "td")
                        logger.debug(f"Row {row_idx}: {len(cells)} cells")
                        
                        if len(cells) >= 1:  # At least one cell
                            issue_data = {}
                            
                            try:
                                # Look for issue ID link in any cell
                                issue_link = None
                                issue_id = None
                                issue_url = None
                                
                                for cell_idx, cell in enumerate(cells):
                                    # Look for issue links
                                    links = cell.find_elements(By.CSS_SELECTOR, "a[href*='/issues/']")
                                    for link in links:
                                        href = link.get_attribute("href")
                                        # Extract issue ID from URL
                                        id_match = re.search(r'/issues/(\d+)', href)
                                        if id_match:
                                            issue_id = id_match.group(1)
                                            issue_url = href
                                            issue_link = link
                                            logger.debug(f"Found issue #{issue_id} in cell {cell_idx}")
                                            break
                                    if issue_link:
                                        break
                                
                                if issue_id and issue_url:
                                    issue_data['id'] = issue_id
                                    issue_data['url'] = issue_url
                                    
                                    # Try to get subject from the link text or nearby elements
                                    subject = issue_link.text.strip()
                                    if subject and not subject.startswith('#') and subject != issue_id:
                                        issue_data['subject'] = subject
                                    else:
                                        # Link text is just the ID, look for subject in adjacent cells
                                        subject_found = False
                                        
                                        # Look for subject in adjacent cells (skip project column)
                                        if not subject_found:
                                            try:
                                                # Find the cell containing the issue link
                                                link_cell = issue_link.find_element(By.XPATH, "ancestor::td[1]")
                                                # Look for subject in next cells
                                                next_cells = link_cell.find_elements(By.XPATH, "following-sibling::td")
                                                for cell_idx, next_cell in enumerate(next_cells[:5]):  # Check first 5 following cells
                                                    cell_text = next_cell.text.strip()
                                                    # Skip empty cells, status/priority keywords, and project names
                                                    skip_keywords = ['New', 'Open', 'Closed', 'Resolved', 'In Progress', 'Low', 'Normal', 'High', 'Urgent', 'Immediate', 
                                                                   'hoge-project', 'fuga-project', 'Bug', 'Feature', 'Task', 'Support']
                                                    
                                                    if (cell_text and len(cell_text) > 3 and 
                                                        cell_text not in skip_keywords and
                                                        not cell_text.endswith('-project')):
                                                        
                                                        # Check if this cell contains a subject link (likely the actual issue title)
                                                        subject_links = next_cell.find_elements(By.TAG_NAME, "a")
                                                        if subject_links:
                                                            for subj_link in subject_links:
                                                                subj_text = subj_link.text.strip()
                                                                # Make sure it's not just the issue ID or project name
                                                                if (subj_text and not subj_text.startswith('#') and 
                                                                    subj_text != issue_id and 
                                                                    not subj_text.endswith('-project') and
                                                                    subj_text not in skip_keywords):
                                                                    issue_data['subject'] = subj_text
                                                                    subject_found = True
                                                                    logger.debug(f"Found subject from link in cell {cell_idx}: {subj_text}")
                                                                    break
                                                        
                                                        # If no links but cell has meaningful text (not project name)
                                                        if not subject_found and cell_idx > 0:  # Skip first cell which might be project
                                                            issue_data['subject'] = cell_text
                                                            subject_found = True
                                                            logger.debug(f"Found subject from cell text {cell_idx}: {cell_text}")
                                                        
                                                        if subject_found:
                                                            break
                                            except Exception:
                                                pass
                                    
                                    # Extract other information from cells using class attributes
                                    for cell_idx, cell in enumerate(cells):
                                        cell_text = cell.text.strip()
                                        cell_class = cell.get_attribute('class') or ''
                                        logger.debug(f"Cell {cell_idx}: '{cell_text}' (class: {cell_class})")
                                        
                                        if cell_text:
                                            # Use class attribute to identify cell type
                                            if 'tracker' in cell_class and not issue_data.get('tracker'):
                                                issue_data['tracker'] = cell_text
                                                logger.debug(f"Found tracker from class in cell {cell_idx}: {cell_text}")
                                            elif 'status' in cell_class and not issue_data.get('status'):
                                                issue_data['status'] = cell_text
                                            elif 'priority' in cell_class and not issue_data.get('priority'):
                                                issue_data['priority'] = cell_text
                                    
                                    # If we still don't have a subject, use a default
                                    if 'subject' not in issue_data:
                                        issue_data['subject'] = f"Issue #{issue_id}"
                                    
                                    issues.append(issue_data)
                                    logger.debug(f"Added issue: {issue_data}")
                                
                            except Exception as e:
                                logger.debug(f"Error processing row {row_idx}: {e}")
                                continue
                else:
                    logger.debug("No issues table found with any selector")
                            
            except Exception as e:
                logger.debug(f"Error processing issues table: {e}")
            
            # If no issues but we have a total count, there might be a parsing issue
            if not issues and total_count > 0:
                logger.warning(f"Found {total_count} issues according to count, but could not parse any issue data")
                # Add debug information
                try:
                    page_source_snippet = self.driver.page_source[:2000]  # First 2000 chars
                    logger.debug(f"Page source snippet: {page_source_snippet}")
                except Exception:
                    pass
            
            # Get pagination parameters
            page = kwargs.get('page', 1)
            
            # Check if there is a next page based on pagination element
            has_next = self._has_next_page()
            
            logger.info(f"Found {len(issues)} issues on page {page}, total: {total_count}, has_next: {has_next}")
            
            # If we have issues but no total count, estimate from issues found
            if issues and total_count == 0:
                total_count = len(issues)
                logger.debug(f"Estimated total count from found issues: {total_count}")
            
            issue_infos = [IssueInfo(**issue) for issue in issues]
            response = IssuesResponse(
                success=True,
                message=f"Found {total_count} issues (showing page {page}){' - more pages available' if has_next else ''}",
                issues=issue_infos,
                total_count=total_count,
                current_page=page,
                has_next=has_next
            )
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Error searching issues: {e}")
            response = IssuesResponse(
                success=False,
                message=f"Error searching issues: {str(e)}",
                issues=[],
                total_count=0,
                current_page=kwargs.get('page', 1)
            )
            return response.model_dump()
    
    def get_issue_details(self, issue_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific issue
        
        Args:
            issue_id: Issue ID to retrieve details for
            
        Returns:
            Dict with issue details
        """
        if not self.is_authenticated or not self.driver:
            response = IssueDetailResponse(
                success=False,
                message='Not authenticated. Please login first.',
                issue=IssueInfo(id=issue_id, subject="", description="")
            )
            return response.model_dump()
        
        try:
            logger.info(f"Fetching details for issue #{issue_id}")
            
            # Navigate to issue page
            issue_url = f"{config.base_url}/issues/{issue_id}"
            self.driver.get(issue_url)
            
            # Wait for page to load

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                response = IssueDetailResponse(
                    success=False,
                    message='Session expired. Please login again.',
                    issue=None
                )
                return response.model_dump()
            
            # Check if issue exists
            if '404' in self.driver.page_source or 'not found' in self.driver.page_source.lower():
                response = IssueDetailResponse(
                    success=False,
                    message=f'Issue #{issue_id} not found.',
                    issue=IssueInfo(id=issue_id, subject="", description="")
                )
                return response.model_dump()
            
            issue_details = {'id': issue_id}
            
            # Extract subject from specific selector
            try:
                subject_elem = self.driver.find_element(By.CSS_SELECTOR, ".subject h3")
                issue_details['subject'] = subject_elem.text.strip()
            except NoSuchElementException:
                pass
            
            # Extract tracker from specific selector
            try:
                tracker_elem = self.driver.find_element(By.CSS_SELECTOR, "#content > h2")
                tracker_text = tracker_elem.text.strip()
                # Extract tracker name from "Tracker Name #IssueID" format
                tracker_match = re.match(r'^([^#]+)\s*#\d+', tracker_text)
                if tracker_match:
                    issue_details['tracker'] = tracker_match.group(1).strip()
            except NoSuchElementException:
                pass
            
            # Extract status from specific selector
            try:
                status_elem = self.driver.find_element(By.CSS_SELECTOR, "div.status.attribute > div.value")
                issue_details['status'] = status_elem.text.strip()
            except NoSuchElementException:
                pass
            
            # Extract priority from specific selector
            try:
                priority_elem = self.driver.find_element(By.CSS_SELECTOR, "div.priority.attribute > div.value")
                issue_details['priority'] = priority_elem.text.strip()
            except NoSuchElementException:
                pass
            
            # Extract all fields from div.attribute elements
            custom_fields = {}
            try:
                attribute_divs = self.driver.find_elements(By.CSS_SELECTOR, "div.attribute")
                # Process attribute divs
                for div in attribute_divs:
                    try:
                        # Get label and value elements
                        label_elem = div.find_element(By.CSS_SELECTOR, "div.label")
                        value_elem = div.find_element(By.CSS_SELECTOR, "div.value")
                        
                        field_name_raw = label_elem.text.strip()
                        field_value = value_elem.text.strip()
                        
                        # Clean field value - take only the first line if it's multi-line
                        if '\n' in field_value:
                            field_value = field_value.split('\n')[0].strip()
                        
                        # Skip empty field names (but allow empty values)
                        if not field_name_raw:
                            continue
                        
                        # Create field key by cleaning the field name
                        field_key = field_name_raw.lower().replace(':', '').replace(' ', '_').replace('　', '_')
                        
                        # Store in issue_details for known fields
                        issue_details[field_key] = field_value
                        
                        # Also store as custom field if it's not a standard field
                        standard_fields = ['status', 'priority', 'assigned_to', 'category', 
                                         'target_version', 'start_date', 'due_date', 'estimated_time', 
                                         'done_ratio', 'spent_time', 'progress']
                        
                        # Also check common Japanese field names
                        japanese_standard_fields = ['ステータス', '優先度', '担当者', 'カテゴリ', 
                                                  '対象バージョン', '開始日', '期日', '予定工数', 
                                                  '進捗率', 'spent_time', '進捗']
                        
                        # Check if this is a custom field by examining the div's CSS classes
                        custom_field_id = None
                        div_classes = div.get_attribute("class") or ""
                        
                        # Look for cf_{id} pattern in CSS classes
                        cf_match = re.search(r'cf_(\d+)', div_classes)
                        if cf_match:
                            custom_field_id = cf_match.group(1)
                        
                        # If we found a custom field ID, use cf_{id} format
                        if custom_field_id:
                            custom_fields[f"cf_{custom_field_id}"] = field_value
                            logger.debug(f"Custom field: cf_{custom_field_id} = '{field_value}'")
                        elif (field_key not in standard_fields and 
                              field_name_raw.rstrip(':') not in japanese_standard_fields):
                            # Fallback: use original label name if no ID found and not a standard field
                            custom_fields[field_name_raw] = field_value
                            logger.debug(f"Custom field (fallback): '{field_name_raw}' = '{field_value}'")
                        
                        logger.debug(f"Field: '{field_name_raw}' -> '{field_key}' = '{field_value}' (classes: {div_classes})")
                        
                    except Exception as e:
                        logger.debug(f"Error processing attribute div: {e}")
                        continue
                        

                        
            except Exception as e:
                logger.debug(f"Error finding detail rows: {e}")
            
            # Description
            try:
                desc_elem = self.driver.find_element(By.CSS_SELECTOR, ".description .wiki, .issue-description .wiki")
                issue_details['description'] = desc_elem.text.strip()
            except NoSuchElementException:
                pass
            
            # Created and Updated dates
            try:
                created_elem = self.driver.find_element(By.CSS_SELECTOR, ".created-on, .author")
                created_text = created_elem.text.strip()
                # Clean created text - take only the first line if it's multi-line
                if '\n' in created_text:
                    created_text = created_text.split('\n')[0].strip()
                issue_details['created_on'] = created_text
            except NoSuchElementException:
                pass
            
            try:
                updated_elem = self.driver.find_element(By.CSS_SELECTOR, ".updated-on")
                issue_details['updated_on'] = updated_elem.text.strip()
            except NoSuchElementException:
                pass
            
            logger.info(f"Successfully retrieved details for issue #{issue_id}: {list(issue_details.keys())}")
            
            # Create IssueInfo object from collected details
            issue_info = IssueInfo(
                id=issue_details.get('id', issue_id),
                subject=issue_details.get('subject', ''),
                description=issue_details.get('description', ''),
                tracker=issue_details.get('tracker', ''),
                status=issue_details.get('status', ''),
                priority=issue_details.get('priority', ''),
                assigned_to=issue_details.get('assigned_to', ''),
                category=issue_details.get('category', ''),
                target_version=issue_details.get('target_version', ''),
                start_date=issue_details.get('start_date', ''),
                due_date=issue_details.get('due_date', ''),
                estimated_time=issue_details.get('estimated_time', ''),
                created_on=issue_details.get('created_on', ''),
                updated_on=issue_details.get('updated_on', ''),
                progress=issue_details.get('done_ratio', ''),
                spent_time=issue_details.get('spent_time', ''),
                custom_fields=custom_fields if custom_fields else None
            )
            
            response = IssueDetailResponse(
                success=True,
                message=f'Successfully retrieved details for issue #{issue_id}',
                issue=issue_info
            )
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Error fetching issue details: {e}")
            response = IssueDetailResponse(
                success=False,
                message=f"Error fetching issue details: {str(e)}",
                issue=IssueInfo(id=issue_id, subject="", description="")
            )
            return response.model_dump()
    
    def get_available_trackers(self, project_id: str = None) -> Dict[str, Any]:
        """
        Get available tracker options from issue creation page
        
        Args:
            project_id: Project ID to get trackers for (optional)
            
        Returns:
            Dict with available tracker options
        """
        if not self.is_authenticated or not self.driver:
            response = TrackersResponse(
                success=False,
                message='Not authenticated. Please login first.',
                trackers=[]
            )
            return response.model_dump()
        
        try:
            logger.info(f"Getting available trackers for project: {project_id or 'all'}")
            
            # If project_id is provided, verify it exists first
            if project_id:
                is_valid, error_msg, _ = self._validate_project_id(project_id)
                if not is_valid:
                    response = TrackersResponse(
                        success=False,
                        message=error_msg,
                        trackers=[]
                    )
                    return response.model_dump()
            
            # Navigate to new issue page
            if project_id:
                new_issue_url = f"{config.base_url}/projects/{project_id}/issues/new"
            else:
                new_issue_url = f"{config.base_url}/issues/new"
            
            self.driver.get(new_issue_url)
            
            # Wait for page to load
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                response = TrackersResponse(
                    success=False,
                    message='Session expired. Please login again.',
                    trackers=[]
                )
                return response.model_dump()
            
            # Get tracker options
            try:
                tracker_select = self.driver.find_element(By.ID, "issue_tracker_id")
                from selenium.webdriver.support.ui import Select
                select = Select(tracker_select)
                
                # First collect all tracker info
                tracker_options = []
                for option in select.options:
                    value = option.get_attribute('value')
                    text = option.text.strip()
                    if value:  # Skip empty values
                        tracker_options.append({
                            'value': value,
                            'text': text
                        })
                
                # Then get fields for each tracker
                available_trackers = []
                for tracker_option in tracker_options:
                    tracker_info = {
                        'id': tracker_option['value'],
                        'name': tracker_option['text']
                    }
                    
                    # Get fields for this tracker if project_id is provided
                    if project_id:
                        try:
                            fields_result = self.get_tracker_fields(project_id, tracker_option['value'])
                            if fields_result.get('success'):
                                tracker_info['fields'] = fields_result.get('fields', [])
                                tracker_info['required_fields'] = fields_result.get('required_fields', [])
                                tracker_info['optional_fields'] = fields_result.get('optional_fields', [])
                            else:
                                logger.debug(f"Could not get fields for tracker {tracker_option['value']}: {fields_result.get('message')}")
                        except Exception as e:
                            logger.debug(f"Error getting fields for tracker {tracker_option['value']}: {e}")
                    
                    available_trackers.append(tracker_info)
                
                logger.info(f"Found {len(available_trackers)} available trackers")
                
                tracker_infos = [TrackerInfo(**tracker) for tracker in available_trackers]
                response = TrackersResponse(
                    success=True,
                    message=f'Found {len(available_trackers)} available trackers' + (f' for project: {project_id}' if project_id else ''),
                    trackers=tracker_infos
                )
                return response.model_dump()
                
            except NoSuchElementException:
                response = TrackersResponse(
                    success=False,
                    message='Tracker field not found on new issue page.',
                    trackers=[]
                )
                return response.model_dump()
            
        except Exception as e:
            logger.error(f"Error getting available trackers: {e}")
            response = TrackersResponse(
                success=False,
                message=f"Error getting available trackers: {str(e)}",
                trackers=[]
            )
            return response.model_dump()
    
    def get_tracker_fields(self, project_id: str, tracker_id: str) -> Dict[str, Any]:
        """
        Get available fields for a specific tracker from new issue page
        
        Args:
            project_id: Project ID
            tracker_id: Tracker ID (required)
            
        Returns:
            Dict following FieldsResponse schema
        """
        if not self.is_authenticated or not self.driver:
            response = FieldsResponse(
                success=False,
                message='Not authenticated. Please login first.',
                fields=[]
            )
            return response.model_dump()
        
        try:
            logger.info(f"Getting tracker fields for project {project_id}, tracker {tracker_id}")
            
            # Navigate to new issue page with tracker_id in URL
            new_issue_url = f"{config.base_url}/projects/{project_id}/issues/new?issue[tracker_id]={tracker_id}"
            
            self.driver.get(new_issue_url)
            
            # Wait for page to load

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                response = FieldsResponse(
                    success=False,
                    message='Session expired. Please login again.',
                    fields=[]
                )
                return response.model_dump()
            
            fields = []
            
            # Scan all form elements dynamically
            form_elements = self.driver.find_elements(By.CSS_SELECTOR, "input, select, textarea")
            
            for element in form_elements:
                try:
                    element_id = element.get_attribute('id')
                    element_name = element.get_attribute('name')
                    element_type = element.get_attribute('type') or element.tag_name
                    
                    # Skip elements without ID or name, or system elements
                    if not element_id and not element_name:
                        continue
                    if element_id and element_id.startswith(('utf8', 'authenticity_token', 'commit')):
                        continue
                    
                    # Use ID if available, otherwise use name
                    field_id = element_id or element_name
                    
                    # Skip if already processed
                    if any(f['id'] == field_id for f in fields):
                        continue
                    
                    # Get field label
                    field_label = self._get_field_label(element, field_id)
                    
                    # Check if field is required
                    is_required = self._is_field_required(element, field_id)
                    
                    # Determine field type and get additional properties
                    field_info = {
                        'id': field_id,
                        'name': field_label,
                        'type': element_type,
                        'required': is_required,
                        'visible': element.is_displayed(),
                        'enabled': element.is_enabled()
                    }
                    
                    # Get additional properties based on field type
                    if element_type == 'select':
                        try:
                            from selenium.webdriver.support.ui import Select
                            select = Select(element)
                            options = []
                            for option in select.options:
                                value = option.get_attribute('value')
                                text = option.text.strip()
                                if value or text:  # Include options with value or text
                                    options.append({'value': value or '', 'text': text})
                            field_info['options'] = options
                            field_info['value_type'] = 'select'
                        except:
                            field_info['options'] = []
                            field_info['value_type'] = 'select'
                    
                    elif element_type in ['input', 'text', 'number', 'date', 'email', 'url']:
                        input_type = element.get_attribute('type') or 'text'
                        field_info['input_type'] = input_type
                        field_info['value_type'] = input_type
                        
                        # Get placeholder if available
                        placeholder = element.get_attribute('placeholder')
                        if placeholder:
                            field_info['placeholder'] = placeholder
                            
                        # Get min/max for number fields
                        if input_type in ['number', 'range']:
                            min_val = element.get_attribute('min')
                            max_val = element.get_attribute('max')
                            if min_val:
                                field_info['min'] = min_val
                            if max_val:
                                field_info['max'] = max_val
                    
                    elif element_type == 'textarea':
                        field_info['value_type'] = 'text'
                        rows = element.get_attribute('rows')
                        cols = element.get_attribute('cols')
                        if rows:
                            field_info['rows'] = rows
                        if cols:
                            field_info['cols'] = cols
                    
                    elif element_type in ['checkbox', 'radio']:
                        field_info['value_type'] = 'boolean' if element_type == 'checkbox' else 'choice'
                    
                    else:
                        field_info['value_type'] = 'string'
                    
                    # Mark custom fields
                    if field_id and ('custom_field' in field_id or field_id.startswith('issue_custom_field')):
                        field_info['custom'] = True
                    else:
                        field_info['custom'] = False
                    
                    fields.append(field_info)
                    logger.debug(f"Found field: {field_label} ({element_type}) - Required: {is_required}")
                    
                except Exception as e:
                    logger.debug(f"Error processing element: {e}")
                    continue
            
            # Separate required and optional fields
            required_fields = [f for f in fields if f['required']]
            optional_fields = [f for f in fields if not f['required']]
            custom_fields = [f for f in fields if f.get('custom', False)]
            standard_fields = [f for f in fields if not f.get('custom', False)]
            
            logger.info(f"Found {len(fields)} total fields: {len(required_fields)} required, {len(optional_fields)} optional, {len(custom_fields)} custom")
            
            field_infos = [FieldInfo(**field) for field in fields]
            response = FieldsResponse(
                success=True,
                message=f'Found {len(fields)} fields ({len(required_fields)} required, {len(optional_fields)} optional, {len(custom_fields)} custom)',
                fields=field_infos
            )
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Error getting tracker fields: {e}")
            response = FieldsResponse(
                success=False,
                message=f"Error getting tracker fields: {str(e)}",
                fields=[]
            )
            return response.model_dump()
    
    def _get_field_label(self, element, field_id: str) -> str:
        """Get field label from various sources"""
        try:
            # Method 1: Look for label with for attribute
            label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
            label_text = label.text.strip().replace('*', '').strip()
            if label_text:
                return label_text
        except:
            pass
        
        try:
            # Method 2: Look for parent label
            parent = element.find_element(By.XPATH, "..")
            label = parent.find_element(By.TAG_NAME, "label")
            label_text = label.text.strip().replace('*', '').strip()
            if label_text:
                return label_text
        except:
            pass
        
        try:
            # Method 3: Look for preceding label
            label = element.find_element(By.XPATH, "preceding-sibling::label[1]")
            label_text = label.text.strip().replace('*', '').strip()
            if label_text:
                return label_text
        except:
            pass
        
        # Method 4: Use field ID as fallback
        if field_id:
            return field_id.replace('issue_', '').replace('_', ' ').title()
        
        return "Unknown Field"
    
    def _is_field_required(self, element, field_id: str) -> bool:
        """Check if field is required"""
        # Method 1: Check required attribute
        if element.get_attribute('required'):
            return True
        
        try:
            # Method 2: Check for required class or asterisk in label
            label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
            if label.find_elements(By.CSS_SELECTOR, ".required, .req"):
                return True
            if '*' in label.text:
                return True
        except:
            pass
        
        try:
            # Method 3: Check parent container for required class
            parent = element.find_element(By.XPATH, "..")
            if 'required' in parent.get_attribute('class') or '':
                return True
        except:
            pass
        
        return False
    
    def _has_next_page(self) -> bool:
        """
        Check if there is a next page by looking for the next page navigation element
        
        Returns:
            bool: True if next page exists, False otherwise
        """
        try:
            # Look for next page link in pagination
            next_page_element = self.driver.find_element(By.CSS_SELECTOR, "#content > span > ul > li.next.page")
            # Check if the element exists and is not disabled
            if next_page_element and next_page_element.is_enabled():
                return True
        except NoSuchElementException:
            logger.debug("No next page element found")
        except Exception as e:
            logger.debug(f"Error checking for next page: {e}")
        
        return False
    
    def get_creation_statuses(self, project_id: str, tracker_id: str) -> Dict[str, Any]:
        """
        Get available status options from new issue creation page for a specific tracker
        
        Args:
            project_id: Project ID
            tracker_id: Tracker ID
            
        Returns:
            Dict with available status options for creation
        """
        if not self.is_authenticated or not self.driver:
            response = StatusesResponse(
                success=False,
                message='Not authenticated. Please login first.',
                statuses=[]
            )
            return response.model_dump()
        
        try:
            logger.info(f"Getting creation statuses for project {project_id}, tracker {tracker_id}")
            
            # Navigate to new issue page with tracker_id
            new_issue_url = f"{config.base_url}/projects/{project_id}/issues/new?issue[tracker_id]={tracker_id}"
            self.driver.get(new_issue_url)
            
            # Wait for page to load

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                response = StatusesResponse(
                    success=False,
                    message='Session expired. Please login again.',
                    statuses=[]
                )
                return response.model_dump()
            
            # Get status options
            try:
                status_select = self.driver.find_element(By.ID, "issue_status_id")
                from selenium.webdriver.support.ui import Select
                select = Select(status_select)
                
                available_statuses = []
                for option in select.options:
                    value = option.get_attribute('value')
                    text = option.text.strip()
                    if value:  # Skip empty values
                        status_info = StatusInfo(
                            value=value,
                            text=text
                        )
                        available_statuses.append(status_info)
                
                logger.info(f"Found {len(available_statuses)} creation statuses")
                
                response = StatusesResponse(
                    success=True,
                    message=f'Found {len(available_statuses)} creation statuses for tracker {tracker_id}',
                    statuses=available_statuses
                )
                return response.model_dump()
                
            except NoSuchElementException:
                response = StatusesResponse(
                    success=False,
                    message='Status field not found on new issue page.',
                    statuses=[]
                )
                return response.model_dump()
            
        except Exception as e:
            logger.error(f"Error getting creation statuses: {e}")
            response = StatusesResponse(
                success=False,
                message=f"Error getting creation statuses: {str(e)}",
                statuses=[]
            )
            return response.model_dump()
    
    def get_available_statuses(self, issue_id: str) -> Dict[str, Any]:
        """
        Get available status options for a specific issue
        
        Args:
            issue_id: Issue ID to get available statuses for
            
        Returns:
            Dict following StatusesResponse schema
        """
        if not self.is_authenticated or not self.driver:
            response = StatusesResponse(
                success=False,
                message='Not authenticated. Please login first.',
                statuses=[]
            )
            return response.model_dump()
        
        try:
            logger.info(f"Getting available statuses for issue #{issue_id}")
            
            # Navigate to issue edit page
            edit_url = f"{config.base_url}/issues/{issue_id}/edit"
            self.driver.get(edit_url)
            
            # Wait for page to load

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                return {
                    'success': False,
                    'message': 'Session expired. Please login again.',
                    'statuses': []
                }
            
            # Check if edit page is accessible
            if '404' in self.driver.page_source or 'not found' in self.driver.page_source.lower():
                response = StatusesResponse(
                    success=False,
                    message=f'Issue #{issue_id} not found or not editable.',
                    statuses=[]
                )
                return response.model_dump()
            
            # Get status options
            try:
                status_select = self.driver.find_element(By.ID, "issue_status_id")
                from selenium.webdriver.support.ui import Select
                select = Select(status_select)
                
                available_statuses = []
                for option in select.options:
                    value = option.get_attribute('value')
                    text = option.text.strip()
                    if value:  # Skip empty values
                        status_info = StatusInfo(
                            value=value,
                            text=text
                        )
                        available_statuses.append(status_info)
                
                logger.info(f"Found {len(available_statuses)} available statuses")
                
                response = StatusesResponse(
                    success=True,
                    message=f'Found {len(available_statuses)} available statuses for issue #{issue_id}',
                    statuses=available_statuses
                )
                return response.model_dump()
                
            except NoSuchElementException:
                response = StatusesResponse(
                    success=False,
                    message='Status field not found on edit page.',
                    statuses=[]
                )
                return response.model_dump()
            
        except Exception as e:
            logger.error(f"Error getting available statuses: {e}")
            response = StatusesResponse(
                success=False,
                message=f"Error getting available statuses: {str(e)}",
                statuses=[]
            )
            return response.model_dump()
    
    def create_issue(self, project_id: str, issue_tracker_id: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new issue in Redmine
        
        Args:
            project_id: Project ID to create issue in
            issue_tracker_id: Tracker ID (required)
            issue_subject: Issue subject/title (text)
            issue_description: Issue description (textarea)
            issue_status_id: Status ID (select-one)
            issue_priority_id: Priority ID (select-one)
            issue_assigned_to_id: Assignee user ID (select-one)
            issue_parent_issue_id: Parent issue ID (text)
            issue_start_date: Start date YYYY-MM-DD (date)
            issue_due_date: Due date YYYY-MM-DD (date)
            issue_is_private: Private flag (checkbox)
            issue[watcher_user_ids][]: Watcher user IDs (checkbox)
            
        Returns:
            Dict following CreateIssueResponse schema
        """
        if not self.is_authenticated or not self.driver:
            response = CreateIssueResponse(
                success=False,
                message='Not authenticated. Please login first.'
            )
            return response.model_dump()
        
        try:
            logger.info(f"Creating issue in project {project_id}")
            
            # Tracker ID validation
            tracker_validation = self._validate_tracker_for_project(project_id, issue_tracker_id)
            if not tracker_validation['valid']:
                response = CreateIssueResponse(
                    success=False,
                    message=f"Invalid tracker ID: {tracker_validation['message']}"
                )
                return response.model_dump()
            
            # Add tracker_id to kwargs before validation
            kwargs['issue_tracker_id'] = issue_tracker_id
            
            # Validate fields BEFORE navigating to create page
            validation_result = self._validate_fields(project_id, issue_tracker_id, kwargs)
            if not validation_result['valid']:
                response = CreateIssueResponse(
                    success=False,
                    message=f"Field validation failed: {validation_result['message']}"
                )
                return response.model_dump()
            
            # Navigate to new issue page with tracker_id in URL
            new_issue_url = f"{config.base_url}/projects/{project_id}/issues/new?issue[tracker_id]={issue_tracker_id}"
            
            self.driver.get(new_issue_url)
            
            # Wait for page to load

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                return {
                    'success': False,
                    'message': 'Session expired. Please login again.'
                }
            
            # Check if new issue page is accessible
            if '404' in self.driver.page_source or 'not found' in self.driver.page_source.lower():
                response = CreateIssueResponse(
                    success=False,
                    message=f'Project {project_id} not found or not accessible.'
                )
                return response.model_dump()
            
            # Debug: Log page title and form elements
            logger.debug(f"New issue page title: {self.driver.title}")
            logger.debug(f"Current URL: {self.driver.current_url}")
            
            # Set fields dynamically based on provided field IDs
            fields_set = []
            fields_failed = []
            
            for field_id, field_value in kwargs.items():
                # Skip tracker as it's already set via URL
                if field_id == 'issue_tracker_id':
                    fields_set.append(f"{field_id}={field_value}")
                    continue
                    
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, f"#{field_id}")
                    element_type = element.tag_name.lower()
                    
                    if element_type == 'select':
                        from selenium.webdriver.support.ui import Select
                        select = Select(element)
                        select.select_by_value(str(field_value))
                        fields_set.append(f"{field_id}={field_value}")
                    elif element_type in ['input', 'textarea']:
                        if element.get_attribute('type') == 'checkbox':
                            if field_value:
                                if not element.is_selected():
                                    element.click()
                                    fields_set.append(f"{field_id}=checked")
                        else:
                            element.clear()
                            element.send_keys(str(field_value))
                            fields_set.append(f"{field_id}={field_value}")
                    
                    logger.debug(f"Set field {field_id} = {field_value}")
                except Exception as e:
                    fields_failed.append(f"{field_id}({e})")
                    logger.debug(f"Could not set field {field_id}: {e}")
            
            logger.info(f"Fields set: {fields_set}")
            if fields_failed:
                logger.warning(f"Fields failed: {fields_failed}")
            
            # Submit the form
            try:
                logger.debug("Looking for submit button...")
                
                # Find submit button
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[name=commit]")
                
                logger.debug(f"Submit button found: {submit_button.get_attribute('value')}")
                
                # Submit form
                submit_button.click()
                logger.debug("Submit button clicked")
                
                # Wait for redirect

                self.wait.until(
                    lambda d: '/issues/' in d.current_url or 'new' not in d.current_url
                )
                
                # Check if creation was successful
                current_url = self.driver.current_url
                logger.info(f"URL after submit: {current_url}")
                logger.info(f"Page title after submit: {self.driver.title}")
                
                # Check for error messages first
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".flash.error, .errorExplanation, #errorExplanation")
                if error_elements:
                    error_messages = [elem.text.strip() for elem in error_elements if elem.text.strip()]
                    return {
                        'success': False,
                        'message': f'Issue creation failed: {"; ".join(error_messages)}'
                    }
                
                if '/issues/' in current_url and 'new' not in current_url:
                    # Extract issue ID from URL
                    issue_id_match = re.search(r'/issues/(\d+)', current_url)
                    if issue_id_match:
                        issue_id = issue_id_match.group(1)
                        logger.info(f"Successfully created issue #{issue_id}")
                        
                        return {
                            'success': True,
                            'message': f'Successfully created issue #{issue_id}',
                            'issue_id': issue_id,
                            'issue_url': current_url
                        }
                
                return {
                    'success': False,
                    'message': f'Issue creation may have failed - unexpected redirect to: {current_url}'
                }
                    
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Error submitting form: {str(e)}'
                }
            
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            response = CreateIssueResponse(
                success=False,
                message=f"Error creating issue: {str(e)}"
            )
            return response.model_dump()
    
    def update_issue(self, issue_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update an issue with new field values
        
        Args:
            issue_id: Issue ID to update
            subject: New subject
            description: New description
            status_id: New status ID
            priority_id: New priority ID
            assigned_to_id: New assignee ID
            done_ratio: Progress percentage (0-100)
            notes: Update notes/comment
            
        Returns:
            Dict following UpdateIssueResponse schema
        """
        if not self.is_authenticated or not self.driver:
            response = UpdateIssueResponse(
                success=False,
                message='Not authenticated. Please login first.'
            )
            return response.model_dump()
        
        try:
            logger.info(f"Updating issue #{issue_id} with params: {list(kwargs.keys())}")
            
            # Navigate to issue edit page
            edit_url = f"{config.base_url}/issues/{issue_id}/edit"
            self.driver.get(edit_url)
            
            # Wait for page to load

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                return {
                    'success': False,
                    'message': 'Session expired. Please login again.'
                }
            
            # Check if edit page is accessible
            if '404' in self.driver.page_source or 'not found' in self.driver.page_source.lower():
                return {
                    'success': False,
                    'message': f'Issue #{issue_id} not found or not editable.'
                }
            
            # Tracker field validation (get current issue tracker for validation)
            current_tracker_id = None
            try:
                tracker_select = self.driver.find_element(By.ID, "issue_tracker_id")
                from selenium.webdriver.support.ui import Select
                select = Select(tracker_select)
                current_tracker_id = select.first_selected_option.get_attribute('value')
            except:
                pass
            
            if current_tracker_id:
                # Get current project ID (extract from URL)
                current_project_id = None
                url_match = re.search(r'/projects/([^/]+)/', self.driver.current_url)
                if url_match:
                    current_project_id = url_match.group(1)
                
                if current_project_id:
                    validation_result = self._validate_fields(current_project_id, current_tracker_id, kwargs)
                    if not validation_result['valid']:
                        return {
                            'success': False,
                            'message': f"Field validation failed: {validation_result['message']}"
                        }
            
            updated_fields = []
            
            # Update subject
            if kwargs.get('subject'):
                try:
                    subject_field = self.driver.find_element(By.ID, "issue_subject")
                    subject_field.clear()
                    subject_field.send_keys(kwargs['subject'])
                    updated_fields.append('subject')
                except NoSuchElementException:
                    logger.debug("Subject field not found")
            
            # Update description
            if kwargs.get('description'):
                try:
                    desc_field = self.driver.find_element(By.ID, "issue_description")
                    desc_field.clear()
                    desc_field.send_keys(kwargs['description'])
                    updated_fields.append('description')
                except NoSuchElementException:
                    logger.debug("Description field not found")
            
            # Update status
            if kwargs.get('status_id'):
                try:
                    status_select = self.driver.find_element(By.ID, "issue_status_id")
                    from selenium.webdriver.support.ui import Select
                    select = Select(status_select)
                    select.select_by_value(str(kwargs['status_id']))
                    updated_fields.append('status')
                except Exception as e:
                    logger.debug(f"Status field not found or invalid value: {e}")
            
            # Update priority
            if kwargs.get('priority_id'):
                try:
                    priority_select = self.driver.find_element(By.ID, "issue_priority_id")
                    from selenium.webdriver.support.ui import Select
                    select = Select(priority_select)
                    select.select_by_value(str(kwargs['priority_id']))
                    updated_fields.append('priority')
                except (NoSuchElementException, Exception):
                    logger.debug("Priority field not found or invalid value")
            
            # Update assignee
            if kwargs.get('assigned_to_id'):
                try:
                    assignee_select = self.driver.find_element(By.ID, "issue_assigned_to_id")
                    from selenium.webdriver.support.ui import Select
                    select = Select(assignee_select)
                    select.select_by_value(str(kwargs['assigned_to_id']))
                    updated_fields.append('assigned_to')
                except (NoSuchElementException, Exception):
                    logger.debug("Assignee field not found or invalid value")
            
            # Update progress
            if kwargs.get('done_ratio') is not None:
                try:
                    progress_select = self.driver.find_element(By.ID, "issue_done_ratio")
                    from selenium.webdriver.support.ui import Select
                    select = Select(progress_select)
                    select.select_by_value(str(kwargs['done_ratio']))
                    updated_fields.append('done_ratio')
                except (NoSuchElementException, Exception):
                    logger.debug("Progress field not found or invalid value")
            
            # Add notes/comment
            if kwargs.get('notes'):
                try:
                    notes_field = self.driver.find_element(By.ID, "issue_notes")
                    notes_field.clear()
                    notes_field.send_keys(kwargs['notes'])
                    updated_fields.append('notes')
                except NoSuchElementException:
                    logger.debug("Notes field not found")
            
            if not updated_fields:
                return {
                    'success': False,
                    'message': 'No valid fields provided for update.'
                }
            
            # Submit the form
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][name='commit'], button[type='submit']")
                submit_button.click()
                
                # Wait for redirect

                self.wait.until(
                    lambda d: '/issues/' in d.current_url
                )
                
                # Check if update was successful
                current_url = self.driver.current_url
                if f'/issues/{issue_id}' in current_url or 'issues' in current_url:
                    logger.info(f"Successfully updated issue #{issue_id}, fields: {updated_fields}")
                    
                    # Check for success message or flash notice
                    success_indicators = [
                        "successfully updated", "flash notice", 
                        "notice", "success"
                    ]
                    
                    page_source = self.driver.page_source.lower()
                    update_confirmed = any(indicator in page_source for indicator in success_indicators)
                    
                    return {
                        'success': True,
                        'message': f'Successfully updated issue #{issue_id}' + (' (confirmed)' if update_confirmed else ''),
                        'updated_fields': updated_fields,
                        'redirect_url': current_url
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Update may have failed - unexpected redirect to: {current_url}'
                    }
                    
            except NoSuchElementException:
                return {
                    'success': False,
                    'message': 'Submit button not found.'
                }
            
        except Exception as e:
            logger.error(f"Error updating issue: {e}")
            return {
                'success': False,
                'message': f"Error updating issue: {str(e)}"
            }
    
    def _validate_fields(self, project_id: str, tracker_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fields against tracker field definitions including required field validation
        
        Args:
            project_id: Project ID
            tracker_id: Tracker ID
            fields: Fields to validate
            
        Returns:
            Dict with validation result including required field checks
        """
        try:
            # Get tracker fields
            tracker_fields_result = self.get_tracker_fields(project_id, str(tracker_id))
            
            if not tracker_fields_result.get('success'):
                return {
                    'valid': False,
                    'message': f"Could not get tracker fields: {tracker_fields_result.get('message')}"
                }
            
            all_fields = tracker_fields_result.get('fields', [])
            field_map = {}
            
            # Create field mapping
            for field in all_fields:
                field_id = field['id']
                field_map[field_id] = field
            
            # Check required fields
            required_fields = [f for f in all_fields if f.get('required', False)]
            missing_required = []
            
            for req_field in required_fields:
                field_id = req_field['id']
                
                # Check if required field is provided
                if field_id not in fields:
                    missing_required.append(f"{req_field.get('name', field_id)} ({field_id})")
            
            if missing_required:
                return {
                    'valid': False,
                    'message': f"Missing required fields: {', '.join(missing_required)}"
                }
            
            # Validate each provided field
            invalid_fields = []
            for field_name, field_value in fields.items():
                if field_name not in field_map:
                    invalid_fields.append(f"{field_name} (not available for this tracker)")
                    continue
                
                # Special validation for assignee field
                if field_name == 'issue_assigned_to_id' and field_value:
                    assignee_validation = self._validate_assignee(project_id, field_value)
                    if not assignee_validation['valid']:
                        invalid_fields.append(f"{field_name}: {assignee_validation['message']}")
            
            if invalid_fields:
                available_fields = list(field_map.keys())
                return {
                    'valid': False,
                    'message': f"Invalid fields: {', '.join(invalid_fields)}. Available fields: {', '.join(available_fields)}"
                }
            
            return {'valid': True}
            
        except Exception as e:
            logger.debug(f"Field validation error: {e}")
            return {
                'valid': True,  # Allow operation to proceed if validation fails
                'message': f"Validation error: {str(e)}"
            }
    
    def _validate_assignee(self, project_id: str, assignee_value: str) -> Dict[str, Any]:
        """
        Validate if assignee exists in project members
        
        Args:
            project_id: Project ID
            assignee_value: Assignee ID or name to validate
            
        Returns:
            Dict with validation result
        """
        try:
            # Skip validation for empty values
            if not assignee_value:
                return {'valid': True}
            
            # Get project members
            members_result = self.get_project_members(project_id)
            
            if not members_result.get('success'):
                logger.debug(f"Could not get project members for assignee validation: {members_result.get('message')}")
                return {'valid': True}  # Allow if we can't validate
            
            members = members_result.get('members', [])
            assignee_str = str(assignee_value)
            
            # Check if assignee exists (by ID or name)
            for member in members:
                if (member.get('id') == assignee_str or 
                    member.get('name', '').lower() == assignee_str.lower()):
                    return {'valid': True}
            
            # Create list of available assignees
            available_assignees = []
            for member in members:
                if member.get('id') and member.get('name'):
                    available_assignees.append(f"{member['name']} (ID: {member['id']})")
            
            if available_assignees:
                return {
                    'valid': False,
                    'message': f"Assignee '{assignee_value}' not found in project members. Available: {', '.join(available_assignees[:5])}{'...' if len(available_assignees) > 5 else ''}"
                }
            else:
                return {
                    'valid': False,
                    'message': f"Assignee '{assignee_value}' not found (no project members available)"
                }
                
        except Exception as e:
            logger.debug(f"Error validating assignee: {e}")
            return {
                'valid': True,  # Allow operation to proceed if validation fails
                'message': f"Assignee validation failed: {str(e)}"
            }
    
    def _validate_tracker_for_project(self, project_id: str, tracker_id: str) -> Dict[str, Any]:
        """
        Validate if tracker_id is available for a specific project
        
        Args:
            project_id: Project ID
            tracker_id: Tracker ID or name to validate
            
        Returns:
            Dict with validation result
        """
        try:
            # Get available trackers for the project
            trackers_result = self.get_available_trackers(project_id)
            
            if not trackers_result.get('success'):
                return {
                    'valid': False,
                    'message': f"Could not get tracker options for project {project_id}: {trackers_result.get('message')}"
                }
            
            tracker_options = trackers_result.get('trackers', [])
            
            if not tracker_options:
                return {
                    'valid': False,
                    'message': f"No tracker options found for project {project_id}"
                }
            
            # Check if requested tracker is available
            requested_tracker = str(tracker_id)
            tracker_found = False
            
            for tracker in tracker_options:
                if (tracker['value'] == requested_tracker or 
                    tracker['text'] == requested_tracker or
                    tracker['text'].lower() == requested_tracker.lower()):
                    tracker_found = True
                    break
            
            if tracker_found:
                return {'valid': True}
            else:
                available_options = [f"{t['value']}:{t['text']}" for t in tracker_options]
                return {
                    'valid': False,
                    'message': f"Tracker '{requested_tracker}' is not available for project {project_id}. Available trackers: {', '.join(available_options)}",
                    'available_trackers': tracker_options
                }
                
        except Exception as e:
            logger.debug(f"Error validating tracker for project: {e}")
            return {
                'valid': False,  # Fail validation if we can't check
                'message': f"Tracker validation failed: {str(e)}"
            }
    

    def get_time_entries(self, project_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get time entries (work hours) for a project with optional filters
        
        Args:
            project_id: Project ID to get time entries for
            start_date: Start date for filtering (YYYY-MM-DD format, optional)
            end_date: End date for filtering (YYYY-MM-DD format, optional)
            user_id: User ID to filter by (optional)
            page: Page number for pagination (default: 1)
            
        Returns:
            Dict following TimeEntriesResponse schema
        """
        if not self.is_authenticated or not self.driver:
            response = TimeEntriesResponse(
                success=False,
                message='Not authenticated. Please login first.',
                time_entries=[],
                total_count=0,
                current_page=1
            )
            return response.model_dump()
        
        try:
            logger.info(f"Fetching time entries for project: {project_id}")
            
            # Build time entries URL
            time_entries_url = f"{config.base_url}/projects/{project_id}/time_entries"
            
            # Build filter parameters
            filter_params = ["set_filter=1", "sort=spent_on:desc"]
            
            # Add date range filter if provided
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            
            if start_date or end_date:
                filter_params.extend([
                    "f[]=spent_on",
                    "op[spent_on]=><"
                ])
                if start_date:
                    filter_params.append(f"v[spent_on][]={start_date}")
                if end_date:
                    filter_params.append(f"v[spent_on][]={end_date}")
            
            # Add user filter if provided
            if kwargs.get('user_id'):
                filter_params.extend([
                    "f[]=user_id",
                    "op[user_id]==",
                    f"v[user_id][]={kwargs['user_id']}"
                ])
            
            # Add empty filter field
            filter_params.append("f[]=")
            
            # Add column configuration for time entries
            filter_params.extend([
                "c[]=spent_on",
                "c[]=user",
                "c[]=activity",
                "c[]=issue",
                "c[]=comments",
                "c[]=hours"
            ])
            
            # Add pagination
            page = kwargs.get('page', 1)
            
            # Append parameters to URL
            from urllib.parse import quote
            if filter_params:
                encoded_params = []
                for param in filter_params:
                    if '=' in param:
                        key, value = param.split('=', 1)
                        encoded_params.append(f"{quote(key, safe='[]')}={quote(value, safe='')}")
                    else:
                        encoded_params.append(quote(param, safe='[]'))
                time_entries_url += "?" + "&".join(encoded_params)
            
            logger.debug(f"Time entries URL: {time_entries_url}")
            logger.debug(f"Filter parameters: {kwargs}")
            
            # Navigate to time entries page
            self.driver.get(time_entries_url)
            
            # Wait for page to load

            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                response = TimeEntriesResponse(
                    success=False,
                    message='Session expired. Please login again.',
                    time_entries=[],
                    total_count=0,
                    current_page=page,
                    has_next=False
                )
                return response.model_dump()
            
            # Check if project is accessible
            if '404' in self.driver.page_source or 'not found' in self.driver.page_source.lower():
                response = TimeEntriesResponse(
                    success=False,
                    message=f'Project {project_id} not found or time entries not accessible.',
                    time_entries=[],
                    total_count=0,
                    current_page=page,
                    has_next=False
                )
                return response.model_dump()
            
            time_entries = []
            total_count = 0
            
            # Extract total count from page
            try:
                # Method 1: Look for pagination info with pattern (1-25/101)
                pagination_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".pagination, .paginator, .page-info, .items-info")
                
                for element in pagination_elements:
                    text = element.text.strip()
                    logger.debug(f"Pagination text: {text}")
                    # Look for patterns like "(1-25/101)" or "1-25/101"
                    match = re.search(r'\(?\d+-\d+/(\d+)\)?', text)
                    if match:
                        total_count = int(match.group(1))
                        logger.debug(f"Found total count from pagination: {total_count}")
                        break
                
                # Method 2: Look for "X entries" or similar text
                if total_count == 0:
                    count_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        ".count, .total-count, .entry-count, .results-info")
                    
                    for element in count_elements:
                        text = element.text.strip()
                        # Extract number from text like "101 entries" or "101 items"
                        count_match = re.search(r'(\d+)\s*(?:entries?|items?|results?)', text, re.IGNORECASE)
                        if count_match:
                            total_count = int(count_match.group(1))
                            logger.debug(f"Found total count from text: {total_count}")
                            break
                            
            except Exception as e:
                logger.debug(f"Could not extract total count: {e}")
            
            # Extract time entries from table
            try:
                time_entries_table = self.driver.find_element(By.CSS_SELECTOR, "#content table.list")
                logger.debug("Found time entries table")
                
                rows = time_entries_table.find_elements(By.TAG_NAME, "tr")
                logger.debug(f"Found {len(rows)} rows in time entries table")
                
                # Skip header row - process data rows only
                for row_idx, row in enumerate(rows[1:]):  # Skip first row (header)
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 7:  # Need at least 7 columns (0-6)
                        try:
                            entry_data = {}
                            # cells[0]: checkbox (empty)
                            # cells[1]: Date (spent_on)
                            entry_data['spent_on'] = cells[1].text.strip()
                            # cells[2]: User
                            entry_data['user'] = cells[2].text.strip()
                            # cells[3]: Activity
                            entry_data['activity'] = cells[3].text.strip()
                            # cells[4]: Issue
                            issue_text = cells[4].text.strip()
                            if issue_text:
                                entry_data['issue'] = issue_text
                                # Extract issue ID
                                issue_match = re.search(r'#(\d+)', issue_text)
                                if issue_match:
                                    entry_data['issue_id'] = issue_match.group(1)
                            # cells[5]: Comments
                            comments = cells[5].text.strip()
                            if comments:
                                entry_data['comments'] = comments
                            # cells[6]: Hours
                            entry_data['hours'] = cells[6].text.strip()
                            
                            time_entries.append(entry_data)
                            logger.debug(f"Added time entry: {entry_data}")
                        except Exception as e:
                            logger.debug(f"Error processing row {row_idx}: {e}")
                            continue
                
            except Exception as e:
                logger.debug(f"Error processing time entries table: {e}")
            
            # Check if there is a next page based on pagination element
            has_next = self._has_next_page()
            
            # If we found time entries but no total count, estimate from entries found
            if time_entries and total_count == 0:
                total_count = len(time_entries)
                logger.debug(f"Estimated total count from found entries: {total_count}")
            
            logger.info(f"Found {len(time_entries)} time entries on page {page}, total: {total_count}, has_next: {has_next}")
            
            time_entry_infos = [TimeEntryInfo(**entry) for entry in time_entries]
            response = TimeEntriesResponse(
                success=True,
                message=f"Found {total_count} time entries (showing page {page}){' - more pages available' if has_next else ''}",
                time_entries=time_entry_infos,
                total_count=total_count,
                current_page=page,
                has_next=has_next
            )
            return response.model_dump()
            
        except Exception as e:
            logger.error(f"Error fetching time entries: {e}")
            response = TimeEntriesResponse(
                success=False,
                message=f"Error fetching time entries: {str(e)}",
                time_entries=[],
                total_count=0,
                current_page=kwargs.get('page', 1),
                has_next=False
            )
            return response.model_dump()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
