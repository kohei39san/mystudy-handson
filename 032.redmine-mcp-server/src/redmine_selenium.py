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
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
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
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login to Redmine using Selenium
        
        Args:
            username: Redmine username
            password: Redmine password
            
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
            
            # Navigate to login page
            self.driver.get(config.login_url)
            
            # Wait for login form to load
            wait = WebDriverWait(self.driver, 10)
            
            try:
                # Find username field
                username_field = wait.until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                
                # Find password field
                password_field = self.driver.find_element(By.ID, "password")
                
                # Fill in credentials
                username_field.clear()
                username_field.send_keys(username)
                password_field.clear()
                password_field.send_keys(password)
                
                # Submit form
                login_button = self.driver.find_element(By.ID, "login-submit")
                login_button.click()
                
                logger.info("Credentials submitted, waiting for response...")
                
                # Wait a moment for the form submission to process
                time.sleep(3)
                
                # Wait for authentication to complete by monitoring URL changes
                max_wait = int(os.getenv('TWOFA_WAIT', '300'))
                start_time = time.time()
                last_url = self.driver.current_url
                
                # Check if we're immediately redirected to 2FA
                time.sleep(2)  # Allow initial redirect
                current_url = self.driver.current_url
                
                if 'twofa' in current_url.lower():
                    logger.info("2FA page detected. Please complete authentication manually in the browser.")
                    print("\n" + "="*60)
                    print("TWO-FACTOR AUTHENTICATION REQUIRED")
                    print("Please complete the 2FA process in the opened browser window.")
                    print("The script will automatically continue once authentication is complete.")
                    print("DO NOT CLOSE THE BROWSER WINDOW")
                    print("="*60 + "\n")
                
                # Monitor URL changes without reloading the page
                while time.time() - start_time < max_wait:
                    try:
                        current_url = self.driver.current_url
                        
                        # Check if URL changed (indicating navigation away from login/2FA)
                        if current_url != last_url:
                            logger.debug(f"URL changed from {last_url} to {current_url}")
                            last_url = current_url
                            
                            # If we're no longer on login or 2FA page, check if we can access projects
                            if ('login' not in current_url.lower() and 
                                'twofa' not in current_url.lower()):
                                
                                # Try to navigate to projects page to verify authentication
                                try:
                                    self.driver.get(config.projects_url)
                                    time.sleep(3)  # Wait for page load
                                    
                                    final_url = self.driver.current_url
                                    
                                    # Check if we successfully accessed projects page
                                    if 'login' not in final_url.lower():
                                        # Look for project content and authenticated user indicators
                                        project_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                                            "table.projects, table.list, a[href*='/projects/'], .projects")
                                        
                                        # Also check for logout link or user menu (signs of authentication)
                                        auth_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                                            "a[href*='logout'], #account, .user-menu")
                                        
                                        page_source = self.driver.page_source.lower()
                                        has_project_content = (project_elements or 'projects' in page_source)
                                        has_auth_indicators = (auth_elements or 'logout' in page_source)
                                        
                                        if has_project_content or has_auth_indicators:
                                            self.is_authenticated = True
                                            logger.info(f"Authentication successful - projects page accessible (project_elements: {len(project_elements)}, auth_elements: {len(auth_elements)})")
                                            
                                            # Notify user that authentication is complete
                                            print("\n" + "="*60)
                                            print("AUTHENTICATION SUCCESSFUL!")
                                            print("The visible browser will now close and switch to headless mode.")
                                            print("Processing will continue in the background...")
                                            print("="*60 + "\n")
                                            
                                            # Give user a moment to see the message
                                            time.sleep(2)
                                            
                                            # Switch to headless mode (this will close the visible browser)
                                            self._switch_to_headless()
                                            
                                            return {
                                                'success': True,
                                                'message': 'Successfully logged in to Redmine',
                                                'redirect_url': final_url
                                            }
                                except Exception as e:
                                    logger.debug(f"Error checking projects access: {e}")
                                    # Continue monitoring even if there's an error
                        
                        # Check if we're still on the same page (no navigation happened)
                        # This could mean user is still completing 2FA
                        if 'twofa' in current_url.lower():
                            # Just wait, don't reload
                            pass
                        elif 'login' in current_url.lower():
                            # Still on login page, might be an error or user needs to retry
                            pass
                    
                    except Exception as e:
                        logger.debug(f"Error during URL monitoring: {e}")
                    
                    time.sleep(2)  # Check every 2 seconds
                
                # Timeout reached
                current_url = self.driver.current_url
                logger.warning(f"Authentication not completed within {max_wait} seconds. Final URL: {current_url}")
                return {
                    'success': False,
                    'message': f'Authentication not completed within {max_wait} seconds. Please try again.'
                }
                
            except TimeoutException:
                logger.error("Login form not found or page load timeout")
                return {
                    'success': False,
                    'message': 'Login form not found or page load timeout'
                }
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {
                'success': False,
                'message': f"Login error: {str(e)}"
            }
    
    def get_projects(self) -> Dict[str, Any]:
        """
        Get list of projects from Redmine
        
        Returns:
            Dict with projects list and status
        """
        if not self.is_authenticated or not self.driver:
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.',
                'projects': []
            }
        
        try:
            logger.info(f"Fetching projects from {config.projects_url}")
            
            # Navigate to projects page
            self.driver.get(config.projects_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            
            projects = []
            
            # Check if we're redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                return {
                    'success': False,
                    'message': 'Session expired. Please login again.',
                    'projects': []
                }
            
            # Method 1: Look for project table
            try:
                project_table = self.driver.find_element(By.CSS_SELECTOR, "table.projects, table.list")
                rows = project_table.find_elements(By.TAG_NAME, "tr")
                
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
                    
                    for link in project_links:
                        href = link.get_attribute("href")
                        if href and re.match(r'.*/projects/[^/?]+/?$', href):
                            project_name = link.text.strip()
                            
                            # Filter out navigation links and system links
                            if (project_name and len(project_name) > 1 and
                                project_name.lower() not in ['projects', 'new project', 'settings', '新しいプロジェクト'] and
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
                return {
                    'success': True,
                    'message': f'Successfully retrieved {len(unique_projects)} projects',
                    'projects': unique_projects
                }
            else:
                return {
                    'success': False,
                    'message': 'No projects found on the page',
                    'projects': []
                }
                
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            return {
                'success': False,
                'message': f"Error fetching projects: {str(e)}",
                'projects': []
            }
    
    def get_project_members(self, project_id: str) -> Dict[str, Any]:
        """
        Get project members from project settings page
        
        Args:
            project_id: Project ID to get members for
            
        Returns:
            Dict with project members list
        """
        if not self.is_authenticated or not self.driver:
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.',
                'members': []
            }
        
        try:
            logger.info(f"Getting project members for project: {project_id}")
            
            # Navigate to project members page
            members_url = f"{config.base_url}/projects/{project_id}/settings/members"
            self.driver.get(members_url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                return {
                    'success': False,
                    'message': 'Session expired. Please login again.',
                    'members': []
                }
            
            # Check if members page is accessible
            if '404' in self.driver.page_source or 'not found' in self.driver.page_source.lower():
                return {
                    'success': False,
                    'message': f'Project {project_id} not found or members page not accessible.',
                    'members': []
                }
            
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
            
            return {
                'success': True,
                'message': f'Successfully retrieved {len(members)} project members',
                'members': members,
                'project_id': project_id
            }
            
        except Exception as e:
            logger.error(f"Error getting project members: {e}")
            return {
                'success': False,
                'message': f"Error getting project members: {str(e)}",
                'members': []
            }
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout from Redmine and close browser
        
        Returns:
            Dict with logout status
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
            
            return {
                'success': True,
                'message': 'Successfully logged out from Redmine'
            }
            
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
            
            return {
                'success': True,
                'message': f'Logged out (with warning: {str(e)})'
            }
    
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
            per_page: Items per page (default: 25)
            
        Returns:
            Dict with search results and pagination info
        """
        if not self.is_authenticated or not self.driver:
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.',
                'issues': [],
                'total_count': 0,
                'page': 1,
                'per_page': 25,
                'total_pages': 0
            }
        
        try:
            logger.info("Searching for issues")
            
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
            time.sleep(2)
            
            # Debug: Log page title and current URL
            logger.debug(f"Page title: {self.driver.title}")
            logger.debug(f"Current URL after navigation: {self.driver.current_url}")
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                return {
                    'success': False,
                    'message': 'Session expired. Please login again.',
                    'issues': [],
                    'total_count': 0,
                    'page': kwargs.get('page', 1),
                    'per_page': kwargs.get('per_page', 25),
                    'total_pages': 0
                }
            
            issues = []
            
            # Extract total count from page
            total_count = 0
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
                
                # Method 2: Look for "X issues" text
                if total_count == 0:
                    count_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        ".count, .total-count, .issue-count, .results-info")
                    
                    for element in count_elements:
                        text = element.text.strip()
                        # Extract number from text like "101 issues" or "101件"
                        count_match = re.search(r'(\d+)\s*(?:issues?|件|個|results?)', text, re.IGNORECASE)
                        if count_match:
                            total_count = int(count_match.group(1))
                            logger.debug(f"Found total count from text: {total_count}")
                            break
                
                # Method 3: Look in page source for pagination info
                if total_count == 0:
                    page_source = self.driver.page_source
                    # Look for pagination patterns in HTML
                    match = re.search(r'\((\d+)-(\d+)/(\d+)\)', page_source)
                    if match:
                        total_count = int(match.group(3))
                        logger.debug(f"Found total count from page source: {total_count}")
                            
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
                                        # Link text is just the ID, look for subject elsewhere
                                        subject_found = False
                                        
                                        # Method 1: Look for other links in the same cell
                                        try:
                                            parent_cell = issue_link.find_element(By.XPATH, "..")
                                            other_links = parent_cell.find_elements(By.TAG_NAME, "a")
                                            for other_link in other_links:
                                                if other_link != issue_link:
                                                    other_text = other_link.text.strip()
                                                    if other_text and not other_text.startswith('#') and other_text != issue_id:
                                                        issue_data['subject'] = other_text
                                                        subject_found = True
                                                        break
                                        except Exception:
                                            pass
                                        
                                        # Method 2: Look for subject in adjacent cells (skip project column)
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
                                        
                                        # Method 3: Look for the actual issue title link in the row
                                        if not subject_found:
                                            try:
                                                row = issue_link.find_element(By.XPATH, "ancestor::tr[1]")
                                                # Look specifically for links that go to the same issue (title links)
                                                all_links = row.find_elements(By.TAG_NAME, "a")
                                                for link in all_links:
                                                    if link != issue_link:
                                                        link_href = link.get_attribute("href")
                                                        link_text = link.text.strip()
                                                        
                                                        # Check if this link also points to the same issue (title link)
                                                        if (link_href and f'/issues/{issue_id}' in link_href and 
                                                            link_text and len(link_text) > 3 and 
                                                            not link_text.startswith('#') and 
                                                            not link_text.isdigit() and
                                                            not link_text.endswith('-project') and
                                                            link_text not in ['Edit', 'Delete', 'View', 'Copy', 'hoge-project', 'fuga-project']):
                                                            issue_data['subject'] = link_text
                                                            subject_found = True
                                                            logger.debug(f"Found subject from issue title link: {link_text}")
                                                            break
                                                        
                                                        # Also check for any meaningful text that's not project/system related
                                                        elif (link_text and len(link_text) > 5 and 
                                                              not link_text.startswith('#') and 
                                                              not link_text.isdigit() and
                                                              not link_text.endswith('-project') and
                                                              'project' not in link_text.lower() and
                                                              link_text not in ['Edit', 'Delete', 'View', 'Copy', 'New', 'Open', 'Closed']):
                                                            issue_data['subject'] = link_text
                                                            subject_found = True
                                                            logger.debug(f"Found subject from meaningful link: {link_text}")
                                                            break
                                            except Exception:
                                                pass
                                    
                                    # Extract other information from cells
                                    for cell_idx, cell in enumerate(cells):
                                        cell_text = cell.text.strip()
                                        if cell_text:
                                            # Try to identify cell content by position or content
                                            if cell_idx == 0 and not issue_data.get('tracker'):
                                                # First cell might be tracker or checkbox
                                                if not cell_text.startswith('#') and cell_text not in ['', '✓']:
                                                    issue_data['tracker'] = cell_text
                                            elif 'status' not in issue_data and cell_text in ['New', 'Open', 'Closed', 'Resolved', 'In Progress', '新規', '進行中', '完了']:
                                                issue_data['status'] = cell_text
                                            elif 'priority' not in issue_data and cell_text in ['Low', 'Normal', 'High', 'Urgent', 'Immediate', '低', '通常', '高', '緊急']:
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
            
            # Alternative method: look for any issue links on the page
            if not issues:
                logger.debug("No issues found in table, trying alternative methods")
                try:
                    # Look for any issue links on the page
                    issue_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/issues/']")
                    logger.debug(f"Found {len(issue_links)} issue links on page")
                    
                    seen_ids = set()
                    for link in issue_links:
                        try:
                            href = link.get_attribute("href")
                            issue_id_match = re.search(r'/issues/(\d+)', href)
                            if issue_id_match:
                                issue_id = issue_id_match.group(1)
                                if issue_id not in seen_ids:
                                    seen_ids.add(issue_id)
                                    
                                    link_text = link.text.strip()
                                    subject = link_text if link_text and not link_text.startswith('#') else f"Issue #{issue_id}"
                                    
                                    issues.append({
                                        'id': issue_id,
                                        'subject': subject,
                                        'url': href
                                    })
                                    logger.debug(f"Added issue from link: #{issue_id} - {subject}")
                        except Exception as e:
                            logger.debug(f"Error processing issue link: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error finding issue links: {e}")
            
            # If still no issues but we have a total count, there might be a parsing issue
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
            per_page = kwargs.get('per_page', 25)
            
            # Calculate pagination info
            total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
            
            logger.info(f"Found {len(issues)} issues on page {page}, total: {total_count}")
            
            # If we have issues but no total count, estimate from issues found
            if issues and total_count == 0:
                total_count = len(issues)
                logger.debug(f"Estimated total count from found issues: {total_count}")
            
            return {
                'success': True,
                'message': f'Found {total_count} issues (showing page {page})',
                'issues': issues,
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
            
        except Exception as e:
            logger.error(f"Error searching issues: {e}")
            return {
                'success': False,
                'message': f"Error searching issues: {str(e)}",
                'issues': [],
                'total_count': 0,
                'page': kwargs.get('page', 1),
                'per_page': kwargs.get('per_page', 25),
                'total_pages': 0
            }
    
    def get_issue_details(self, issue_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific issue
        
        Args:
            issue_id: Issue ID to retrieve details for
            
        Returns:
            Dict with issue details
        """
        if not self.is_authenticated or not self.driver:
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.',
                'issue': {}
            }
        
        try:
            logger.info(f"Fetching details for issue #{issue_id}")
            
            # Navigate to issue page
            issue_url = f"{config.base_url}/issues/{issue_id}"
            self.driver.get(issue_url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                return {
                    'success': False,
                    'message': 'Session expired. Please login again.',
                    'issue': {}
                }
            
            # Check if issue exists
            if '404' in self.driver.page_source or 'not found' in self.driver.page_source.lower():
                return {
                    'success': False,
                    'message': f'Issue #{issue_id} not found.',
                    'issue': {}
                }
            
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
                # Extract tracker name from "トラッカー名 #チケットID" format
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
                        
                        # Store the field
                        issue_details[field_key] = field_value
                        
                        logger.debug(f"Field: '{field_name_raw}' -> '{field_key}' = '{field_value}'")
                        
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
            
            return {
                'success': True,
                'message': f'Successfully retrieved details for issue #{issue_id}',
                'issue': issue_details
            }
            
        except Exception as e:
            logger.error(f"Error fetching issue details: {e}")
            return {
                'success': False,
                'message': f"Error fetching issue details: {str(e)}",
                'issue': {}
            }
    
    def get_available_trackers(self, project_id: str = None) -> Dict[str, Any]:
        """
        Get available tracker options from issue creation page
        
        Args:
            project_id: Project ID to get trackers for (optional)
            
        Returns:
            Dict with available tracker options
        """
        if not self.is_authenticated or not self.driver:
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.',
                'trackers': []
            }
        
        try:
            logger.info(f"Getting available trackers for project: {project_id or 'all'}")
            
            # Navigate to new issue page
            if project_id:
                new_issue_url = f"{config.base_url}/projects/{project_id}/issues/new"
            else:
                new_issue_url = f"{config.base_url}/issues/new"
            
            self.driver.get(new_issue_url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                return {
                    'success': False,
                    'message': 'Session expired. Please login again.',
                    'trackers': []
                }
            
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
                        'value': tracker_option['value'],
                        'text': tracker_option['text']
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
                
                return {
                    'success': True,
                    'message': f'Found {len(available_trackers)} available trackers',
                    'trackers': available_trackers
                }
                
            except NoSuchElementException:
                return {
                    'success': False,
                    'message': 'Tracker field not found on new issue page.',
                    'trackers': []
                }
            
        except Exception as e:
            logger.error(f"Error getting available trackers: {e}")
            return {
                'success': False,
                'message': f"Error getting available trackers: {str(e)}",
                'trackers': []
            }
    
    def get_tracker_fields(self, project_id: str, tracker_id: str) -> Dict[str, Any]:
        """
        Get available fields for a specific tracker from new issue page
        
        Args:
            project_id: Project ID
            tracker_id: Tracker ID (required)
            
        Returns:
            Dict with field information including required/optional status and input types
        """
        if not self.is_authenticated or not self.driver:
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.',
                'fields': []
            }
        
        try:
            logger.info(f"Getting tracker fields for project {project_id}, tracker {tracker_id}")
            
            # Navigate to new issue page with tracker_id in URL
            new_issue_url = f"{config.base_url}/projects/{project_id}/issues/new?issue[tracker_id]={tracker_id}"
            
            self.driver.get(new_issue_url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                return {
                    'success': False,
                    'message': 'Session expired. Please login again.',
                    'fields': []
                }
            
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
            
            return {
                'success': True,
                'message': f'Found {len(fields)} fields ({len(required_fields)} required, {len(optional_fields)} optional, {len(custom_fields)} custom)',
                'fields': fields,
                'required_fields': required_fields,
                'optional_fields': optional_fields,
                'custom_fields': custom_fields,
                'standard_fields': standard_fields,
                'tracker_id': tracker_id
            }
            
        except Exception as e:
            logger.error(f"Error getting tracker fields: {e}")
            return {
                'success': False,
                'message': f"Error getting tracker fields: {str(e)}",
                'fields': []
            }
    
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
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.',
                'statuses': []
            }
        
        try:
            logger.info(f"Getting creation statuses for project {project_id}, tracker {tracker_id}")
            
            # Navigate to new issue page with tracker_id
            new_issue_url = f"{config.base_url}/projects/{project_id}/issues/new?issue[tracker_id]={tracker_id}"
            self.driver.get(new_issue_url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Check if redirected to login page
            if 'login' in self.driver.current_url.lower():
                logger.warning("Redirected to login page - session expired")
                self.is_authenticated = False
                return {
                    'success': False,
                    'message': 'Session expired. Please login again.',
                    'statuses': []
                }
            
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
                        available_statuses.append({
                            'value': value,
                            'text': text
                        })
                
                logger.info(f"Found {len(available_statuses)} creation statuses")
                
                return {
                    'success': True,
                    'message': f'Found {len(available_statuses)} creation statuses for tracker {tracker_id}',
                    'statuses': available_statuses
                }
                
            except NoSuchElementException:
                return {
                    'success': False,
                    'message': 'Status field not found on new issue page.',
                    'statuses': []
                }
            
        except Exception as e:
            logger.error(f"Error getting creation statuses: {e}")
            return {
                'success': False,
                'message': f"Error getting creation statuses: {str(e)}",
                'statuses': []
            }
    
    def get_available_statuses(self, issue_id: str) -> Dict[str, Any]:
        """
        Get available status options for a specific issue
        
        Args:
            issue_id: Issue ID to get available statuses for
            
        Returns:
            Dict with available status options
        """
        if not self.is_authenticated or not self.driver:
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.',
                'statuses': []
            }
        
        try:
            logger.info(f"Getting available statuses for issue #{issue_id}")
            
            # Navigate to issue edit page
            edit_url = f"{config.base_url}/issues/{issue_id}/edit"
            self.driver.get(edit_url)
            
            # Wait for page to load
            time.sleep(2)
            
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
                return {
                    'success': False,
                    'message': f'Issue #{issue_id} not found or not editable.',
                    'statuses': []
                }
            
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
                        available_statuses.append({
                            'value': value,
                            'text': text
                        })
                
                logger.info(f"Found {len(available_statuses)} available statuses")
                
                return {
                    'success': True,
                    'message': f'Found {len(available_statuses)} available statuses for issue #{issue_id}',
                    'statuses': available_statuses
                }
                
            except NoSuchElementException:
                return {
                    'success': False,
                    'message': 'Status field not found on edit page.',
                    'statuses': []
                }
            
        except Exception as e:
            logger.error(f"Error getting available statuses: {e}")
            return {
                'success': False,
                'message': f"Error getting available statuses: {str(e)}",
                'statuses': []
            }
    
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
            Dict with creation status
        """
        if not self.is_authenticated or not self.driver:
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.'
            }
        
        try:
            logger.info(f"Creating issue in project {project_id}")
            
            # トラッカーIDバリデーション
            tracker_validation = self._validate_tracker_for_project(project_id, issue_tracker_id)
            if not tracker_validation['valid']:
                return {
                    'success': False,
                    'message': f"Invalid tracker ID: {tracker_validation['message']}"
                }
            
            # Add tracker_id to kwargs before validation
            kwargs['issue_tracker_id'] = issue_tracker_id
            
            # Validate fields BEFORE navigating to create page
            validation_result = self._validate_fields(project_id, issue_tracker_id, kwargs)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': f"Field validation failed: {validation_result['message']}"
                }
            
            # Navigate to new issue page with tracker_id in URL
            new_issue_url = f"{config.base_url}/projects/{project_id}/issues/new?issue[tracker_id]={issue_tracker_id}"
            
            self.driver.get(new_issue_url)
            
            # Wait for page to load
            time.sleep(2)
            
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
                return {
                    'success': False,
                    'message': f'Project {project_id} not found or not accessible.'
                }
            
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
                time.sleep(3)
                
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
            return {
                'success': False,
                'message': f"Error creating issue: {str(e)}"
            }
    
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
            Dict with update status
        """
        if not self.is_authenticated or not self.driver:
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.'
            }
        
        try:
            logger.info(f"Updating issue #{issue_id} with params: {list(kwargs.keys())}")
            
            # Navigate to issue edit page
            edit_url = f"{config.base_url}/issues/{issue_id}/edit"
            self.driver.get(edit_url)
            
            # Wait for page to load
            time.sleep(2)
            
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
            
            # トラッカーフィールドバリデーション（現在のチケットのトラッカーを取得してバリデーション）
            current_tracker_id = None
            try:
                tracker_select = self.driver.find_element(By.ID, "issue_tracker_id")
                from selenium.webdriver.support.ui import Select
                select = Select(tracker_select)
                current_tracker_id = select.first_selected_option.get_attribute('value')
            except:
                pass
            
            if current_tracker_id:
                # 現在のプロジェクトIDを取得（URLから抽出）
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
                time.sleep(3)
                
                # Check if update was successful
                current_url = self.driver.current_url
                if f'/issues/{issue_id}' in current_url or 'issues' in current_url:
                    logger.info(f"Successfully updated issue #{issue_id}, fields: {updated_fields}")
                    
                    # Check for success message or flash notice
                    success_indicators = [
                        "successfully updated", "更新しました", "flash notice", 
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
    

    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass