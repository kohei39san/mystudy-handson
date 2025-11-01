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
                                
                                # Extract roles (usually second column)
                                if len(cells) > 1:
                                    roles_text = cells[1].text.strip()
                                    member_info['roles'] = [role.strip() for role in roles_text.split(',') if role.strip()]
                                
                                # Extract additional info if available
                                if len(cells) > 2:
                                    member_info['additional_info'] = cells[2].text.strip()
                                
                                members.append(member_info)
                                logger.debug(f"Added member: {member_info['name']} (ID: {member_info.get('id', 'unknown')})")
                                
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
                                            'roles': []
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
            
            # Status, Priority, Assignee, etc. from the details table
            try:
                detail_rows = self.driver.find_elements(By.CSS_SELECTOR, "#content > div.issue.details > div.attributes tr")
                # Process table rows
                for row in detail_rows:
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            field_name = cells[0].text.strip().lower().replace(':', '')
                            field_value = cells[1].text.strip()
                            
                            # Clean field value - take only the first line if it's multi-line
                            if '\n' in field_value:
                                field_value = field_value.split('\n')[0].strip()
                            
                            logger.debug(f"Field: '{field_name}' = '{field_value}'")
                            
                            if field_name in ['assigned to', 'assignee', '担当者'] and not issue_details.get('assigned_to'):
                                issue_details['assigned_to'] = field_value
                            elif field_name in ['category', 'カテゴリ'] and not issue_details.get('category'):
                                issue_details['category'] = field_value

                            elif field_name in ['start date', '開始日'] and not issue_details.get('start_date'):
                                issue_details['start_date'] = field_value
                            elif field_name in ['due date', '期日'] and not issue_details.get('due_date'):
                                issue_details['due_date'] = field_value
                            elif field_name in ['% done', '進捗率', 'progress'] and not issue_details.get('done_ratio'):
                                issue_details['done_ratio'] = field_value
                    except Exception as e:
                        logger.debug(f"Error processing row: {e}")
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
                
                available_trackers = []
                for option in select.options:
                    value = option.get_attribute('value')
                    text = option.text.strip()
                    if value:  # Skip empty values
                        available_trackers.append({
                            'value': value,
                            'text': text
                        })
                
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
    
    def get_tracker_fields(self, project_id: str, tracker_id: str = None) -> Dict[str, Any]:
        """
        Get available fields for a specific tracker from new issue page
        
        Args:
            project_id: Project ID
            tracker_id: Tracker ID (optional, if not provided, uses default)
            
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
            logger.info(f"Getting tracker fields for project {project_id}, tracker {tracker_id or 'default'}")
            
            # Navigate to new issue page
            new_issue_url = f"{config.base_url}/projects/{project_id}/issues/new"
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
            
            # Set tracker if specified
            if tracker_id:
                try:
                    tracker_select = self.driver.find_element(By.ID, "issue_tracker_id")
                    from selenium.webdriver.support.ui import Select
                    select = Select(tracker_select)
                    select.select_by_value(str(tracker_id))
                    time.sleep(1)  # Wait for page to update
                except Exception as e:
                    logger.debug(f"Could not set tracker: {e}")
            
            fields = []
            
            # Get all form fields
            form_fields = [
                ('issue_tracker_id', 'select', 'Tracker'),
                ('issue_subject', 'input', 'Subject'),
                ('issue_description', 'textarea', 'Description'),
                ('issue_status_id', 'select', 'Status'),
                ('issue_priority_id', 'select', 'Priority'),
                ('issue_assigned_to_id', 'select', 'Assignee'),
                ('issue_category_id', 'select', 'Category'),
                ('issue_fixed_version_id', 'select', 'Target version'),
                ('issue_parent_issue_id', 'input', 'Parent task'),
                ('issue_start_date', 'input', 'Start date'),
                ('issue_due_date', 'input', 'Due date'),
                ('issue_estimated_hours', 'input', 'Estimated time'),
                ('issue_done_ratio', 'select', '% Done')
            ]
            
            for field_id, field_type, field_label in form_fields:
                try:
                    element = self.driver.find_element(By.ID, field_id)
                    
                    # Check if field is required
                    is_required = False
                    
                    # Method 1: Check required attribute
                    if element.get_attribute('required'):
                        is_required = True
                    
                    # Method 2: Check for required class or parent label
                    try:
                        # Find associated label
                        label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                        if label.find_elements(By.CSS_SELECTOR, ".required, .req"):
                            is_required = True
                        # Check for asterisk in label text
                        if '*' in label.text:
                            is_required = True
                    except:
                        pass
                    
                    # Get field properties
                    field_info = {
                        'id': field_id,
                        'name': field_label,
                        'type': field_type,
                        'required': is_required,
                        'visible': element.is_displayed(),
                        'enabled': element.is_enabled()
                    }
                    
                    # Get additional properties based on field type
                    if field_type == 'select':
                        try:
                            from selenium.webdriver.support.ui import Select
                            select = Select(element)
                            options = []
                            for option in select.options:
                                value = option.get_attribute('value')
                                text = option.text.strip()
                                if value:  # Skip empty values
                                    options.append({'value': value, 'text': text})
                            field_info['options'] = options
                        except:
                            field_info['options'] = []
                    
                    elif field_type == 'input':
                        input_type = element.get_attribute('type') or 'text'
                        field_info['input_type'] = input_type
                        
                        # Get placeholder if available
                        placeholder = element.get_attribute('placeholder')
                        if placeholder:
                            field_info['placeholder'] = placeholder
                    
                    fields.append(field_info)
                    logger.debug(f"Found field: {field_label} ({field_type}) - Required: {is_required}")
                    
                except NoSuchElementException:
                    logger.debug(f"Field {field_id} not found")
                    continue
                except Exception as e:
                    logger.debug(f"Error processing field {field_id}: {e}")
                    continue
            
            # Get custom fields
            try:
                custom_fields = self.driver.find_elements(By.CSS_SELECTOR, "[id^='issue_custom_field_values_']")
                for cf in custom_fields:
                    cf_id = cf.get_attribute('id')
                    cf_name = cf.get_attribute('name')
                    
                    # Try to find label
                    cf_label = "Custom Field"
                    try:
                        label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{cf_id}']")
                        cf_label = label.text.strip().replace('*', '').strip()
                    except:
                        pass
                    
                    # Check if required
                    is_required = bool(cf.get_attribute('required'))
                    try:
                        label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{cf_id}']")
                        if '*' in label.text or label.find_elements(By.CSS_SELECTOR, ".required"):
                            is_required = True
                    except:
                        pass
                    
                    cf_type = cf.tag_name.lower()
                    if cf_type == 'input':
                        cf_type = cf.get_attribute('type') or 'text'
                    
                    field_info = {
                        'id': cf_id,
                        'name': cf_label,
                        'type': cf_type,
                        'required': is_required,
                        'visible': cf.is_displayed(),
                        'enabled': cf.is_enabled(),
                        'custom': True
                    }
                    
                    fields.append(field_info)
                    logger.debug(f"Found custom field: {cf_label} ({cf_type}) - Required: {is_required}")
                    
            except Exception as e:
                logger.debug(f"Error getting custom fields: {e}")
            
            # Separate required and optional fields
            required_fields = [f for f in fields if f['required']]
            optional_fields = [f for f in fields if not f['required']]
            
            logger.info(f"Found {len(required_fields)} required fields and {len(optional_fields)} optional fields")
            
            return {
                'success': True,
                'message': f'Found {len(fields)} fields ({len(required_fields)} required, {len(optional_fields)} optional)',
                'fields': fields,
                'required_fields': required_fields,
                'optional_fields': optional_fields,
                'tracker_id': tracker_id
            }
            
        except Exception as e:
            logger.error(f"Error getting tracker fields: {e}")
            return {
                'success': False,
                'message': f"Error getting tracker fields: {str(e)}",
                'fields': []
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
    
    def create_issue(self, project_id: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new issue in Redmine
        
        Args:
            project_id: Project ID to create issue in
            tracker_id: Tracker ID
            subject: Issue subject/title
            description: Issue description
            status_id: Status ID
            priority_id: Priority ID
            assigned_to_id: Assignee user ID
            parent_issue_id: Parent issue ID
            start_date: Start date (YYYY-MM-DD)
            due_date: Due date (YYYY-MM-DD)
            estimated_hours: Estimated hours
            done_ratio: Progress percentage (0-100)
            
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
            
            # Navigate to new issue page
            new_issue_url = f"{config.base_url}/projects/{project_id}/issues/new"
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
            
            # 必須フィールドの検証
            logger.info("=== 必須フィールドの検証 ===")
            
            # Check for form elements
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            logger.debug(f"Found {len(forms)} forms on page")
            
            # 必須フィールドを検出
            required_fields = []
            
            # フォーム内の必須フィールドを検索
            form_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[required], select[required], textarea[required]")
            for element in form_elements:
                field_name = element.get_attribute('name') or element.get_attribute('id')
                field_type = element.tag_name
                if field_name:
                    required_fields.append(f"{field_name} ({field_type})")
            
            # ラベルで必須マークがあるフィールドも確認
            required_labels = self.driver.find_elements(By.CSS_SELECTOR, "label .required, label.required")
            for label in required_labels:
                label_text = label.text.strip()
                if label_text:
                    required_fields.append(f"Label: {label_text}")
            
            logger.info("検出された必須フィールド:")
            for field in required_fields:
                logger.info(f"  - {field}")
            
            # Look for input fields
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            logger.debug(f"Found {len(inputs)} inputs, {len(selects)} selects, {len(textareas)} textareas")
            
            # Log some field IDs/names for debugging
            for i, inp in enumerate(inputs[:10]):  # First 10 inputs
                inp_id = inp.get_attribute('id')
                inp_name = inp.get_attribute('name')
                inp_type = inp.get_attribute('type')
                logger.debug(f"Input {i}: id='{inp_id}', name='{inp_name}', type='{inp_type}'")
            
            # 必須フィールドチェック: subjectが提供されているか確認
            if not kwargs.get('subject'):
                return {
                    'success': False,
                    'message': 'Subject is required for creating an issue.',
                    'required_fields': required_fields
                }
            
            # トラッカーIDバリデーション
            if kwargs.get('tracker_id'):
                # まずトラッカーIDが有効かチェック
                tracker_validation = self._validate_tracker_for_project(project_id, kwargs['tracker_id'])
                if not tracker_validation['valid']:
                    return {
                        'success': False,
                        'message': f"Invalid tracker ID: {tracker_validation['message']}"
                    }
                
                # フィールドバリデーション
                validation_result = self._validate_fields(project_id, kwargs['tracker_id'], kwargs)
                if not validation_result['valid']:
                    return {
                        'success': False,
                        'message': f"Field validation failed: {validation_result['message']}"
                    }
            
            # Set tracker
            if kwargs.get('tracker_id'):
                try:
                    tracker_select = self.driver.find_element(By.ID, "issue_tracker_id")
                    from selenium.webdriver.support.ui import Select
                    select = Select(tracker_select)
                    select.select_by_value(str(kwargs['tracker_id']))
                except Exception as e:
                    logger.debug(f"Tracker field not found or not accessible: {e}")
            
            # Set subject (required)
            if kwargs.get('subject'):
                try:
                    subject_field = self.driver.find_element(By.ID, "issue_subject")
                    subject_field.clear()
                    subject_field.send_keys(kwargs['subject'])
                except Exception as e:
                    return {
                        'success': False,
                        'message': f"Could not find subject field: {str(e)}"
                    }
            
            # Set description
            if kwargs.get('description'):
                try:
                    desc_field = self.driver.find_element(By.ID, "issue_description")
                    desc_field.clear()
                    desc_field.send_keys(kwargs['description'])
                except Exception:
                    logger.debug("Description field not found or not accessible")
            
            # Set status
            if kwargs.get('status_id'):
                try:
                    status_select = self.driver.find_element(By.ID, "issue_status_id")
                    from selenium.webdriver.support.ui import Select
                    select = Select(status_select)
                    select.select_by_value(str(kwargs['status_id']))
                except Exception:
                    logger.debug("Status field not found or invalid value")
            
            # Set priority
            if kwargs.get('priority_id'):
                try:
                    priority_select = self.driver.find_element(By.ID, "issue_priority_id")
                    from selenium.webdriver.support.ui import Select
                    select = Select(priority_select)
                    select.select_by_value(str(kwargs['priority_id']))
                except Exception:
                    logger.debug("Priority field not found or invalid value")
            
            # Set assignee
            if kwargs.get('assigned_to_id'):
                try:
                    assignee_select = self.driver.find_element(By.ID, "issue_assigned_to_id")
                    from selenium.webdriver.support.ui import Select
                    select = Select(assignee_select)
                    select.select_by_value(str(kwargs['assigned_to_id']))
                except Exception:
                    logger.debug("Assignee field not found or invalid value")
            
            # Set parent issue
            if kwargs.get('parent_issue_id'):
                try:
                    parent_field = self.driver.find_element(By.ID, "issue_parent_issue_id")
                    parent_field.clear()
                    parent_field.send_keys(str(kwargs['parent_issue_id']))
                except Exception:
                    logger.debug("Parent issue field not found")
            
            # Set start date
            if kwargs.get('start_date'):
                try:
                    start_date_field = self.driver.find_element(By.ID, "issue_start_date")
                    start_date_field.clear()
                    start_date_field.send_keys(kwargs['start_date'])
                except Exception:
                    logger.debug("Start date field not found")
            
            # Set due date
            if kwargs.get('due_date'):
                try:
                    due_date_field = self.driver.find_element(By.ID, "issue_due_date")
                    due_date_field.clear()
                    due_date_field.send_keys(kwargs['due_date'])
                except Exception:
                    logger.debug("Due date field not found")
            
            # Set estimated hours
            if kwargs.get('estimated_hours'):
                try:
                    estimated_hours_field = self.driver.find_element(By.ID, "issue_estimated_hours")
                    estimated_hours_field.clear()
                    estimated_hours_field.send_keys(str(kwargs['estimated_hours']))
                except Exception:
                    logger.debug("Estimated hours field not found")
            
            # Set progress
            if kwargs.get('done_ratio') is not None:
                try:
                    progress_select = self.driver.find_element(By.ID, "issue_done_ratio")
                    from selenium.webdriver.support.ui import Select
                    select = Select(progress_select)
                    select.select_by_value(str(kwargs['done_ratio']))
                except Exception:
                    logger.debug("Progress field not found or invalid value")
            
            # Submit the form
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][name='commit'], button[type='submit']")
                submit_button.click()
                
                # Wait for redirect
                time.sleep(3)
                
                # Check if creation was successful
                current_url = self.driver.current_url
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
                
                # Check for error messages
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".flash.error, .errorExplanation, #errorExplanation")
                if error_elements:
                    error_messages = [elem.text.strip() for elem in error_elements if elem.text.strip()]
                    return {
                        'success': False,
                        'message': f'Issue creation failed: {"; ".join(error_messages)}'
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
        Validate fields against tracker field definitions
        
        Args:
            project_id: Project ID
            tracker_id: Tracker ID
            fields: Fields to validate
            
        Returns:
            Dict with validation result
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
            
            # Create field mapping (handle both with and without 'issue_' prefix)
            for field in all_fields:
                field_id = field['id']
                # Remove 'issue_' prefix for mapping
                clean_id = field_id.replace('issue_', '') if field_id.startswith('issue_') else field_id
                field_map[clean_id] = field
                field_map[field_id] = field  # Also keep original ID
            
            # Validate each provided field
            invalid_fields = []
            for field_name, field_value in fields.items():
                # Skip special fields that are always valid
                if field_name in ['subject', 'tracker_id', 'project_id']:
                    continue
                
                if field_name not in field_map:
                    invalid_fields.append(f"{field_name} (not available for this tracker)")
                    continue
                
                # Special validation for assignee field
                if field_name in ['assigned_to_id', 'assignee'] and field_value:
                    assignee_validation = self._validate_assignee(project_id, field_value)
                    if not assignee_validation['valid']:
                        invalid_fields.append(f"{field_name}: {assignee_validation['message']}")
            
            if invalid_fields:
                available_fields = [k for k in field_map.keys() if not k.startswith('issue_')]
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
            # Skip validation for special values
            if assignee_value.lower() in ['me', 'myself', '']:
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
            # Get tracker fields for the project to see available trackers
            tracker_fields_result = self.get_tracker_fields(project_id)
            
            if not tracker_fields_result.get('success'):
                return {
                    'valid': False,
                    'message': f"Could not get tracker options for project {project_id}: {tracker_fields_result.get('message')}"
                }
            
            # Find tracker field and its options
            tracker_options = []
            for field in tracker_fields_result.get('fields', []):
                if field.get('id') == 'issue_tracker_id':
                    tracker_options = field.get('options', [])
                    break
            
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
    
    def _validate_tracker(self, tracker_id: str) -> Dict[str, Any]:
        """
        Validate if tracker_id is available
        
        Args:
            tracker_id: Tracker ID or name to validate
            
        Returns:
            Dict with validation result
        """
        try:
            # Get available trackers
            trackers_result = self.get_available_trackers()
            
            if not trackers_result.get('success'):
                return {
                    'valid': False,
                    'message': f"Could not validate tracker: {trackers_result.get('message')}"
                }
            
            available_trackers = trackers_result.get('trackers', [])
            
            # Check if requested tracker is available
            requested_tracker = str(tracker_id)
            tracker_found = False
            
            for tracker in available_trackers:
                if (tracker['value'] == requested_tracker or 
                    tracker['text'] == requested_tracker or
                    tracker['text'].lower() == requested_tracker.lower()):
                    tracker_found = True
                    break
            
            if tracker_found:
                return {'valid': True}
            else:
                available_options = [f"{t['value']}:{t['text']}" for t in available_trackers]
                return {
                    'valid': False,
                    'message': f"Tracker '{requested_tracker}' is not available. Available trackers: {', '.join(available_options)}",
                    'available_trackers': available_trackers
                }
                
        except Exception as e:
            logger.debug(f"Error validating tracker: {e}")
            return {
                'valid': True,  # Allow search to proceed if validation fails
                'message': f"Tracker validation failed: {str(e)}"
            }
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass