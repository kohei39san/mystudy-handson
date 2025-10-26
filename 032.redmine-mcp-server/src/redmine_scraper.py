"""
Redmine Web Scraper
Handles authentication and data extraction from Redmine via web scraping
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import time
import logging
import webbrowser
from urllib.parse import urljoin, urlparse
import re
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import config with proper error handling
try:
    from config import config
except ImportError:
    try:
        from .config import config
    except ImportError:
        # Fallback to creating a minimal config if import fails
        class MinimalConfig:
            def __init__(self):
                self.base_url = os.getenv('REDMINE_URL', 'http://localhost:3000')
                if self.base_url.endswith('/'):
                    self.base_url = self.base_url[:-1]
                self.login_url = f"{self.base_url}/login"
                self.logout_url = f"{self.base_url}/logout"
                self.projects_url = f"{self.base_url}/projects"
                self.session_timeout = int(os.getenv('SESSION_TIMEOUT', '3600'))
                self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
                self.user_agent = os.getenv('USER_AGENT', 
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                self.default_headers = {
                    'User-Agent': self.user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
                self.retry_delay = float(os.getenv('RETRY_DELAY', '1.0'))
                self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        config = MinimalConfig()

# Set up logging
logging.basicConfig(level=logging.INFO if config.debug else logging.WARNING)
logger = logging.getLogger(__name__)

class RedmineScrapingError(Exception):
    """Custom exception for Redmine scraping errors"""
    pass

class RedmineScraper:
    """Redmine web scraper with session management"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.default_headers)
        self.is_authenticated = False
        self.last_activity = None
        
    def _get_csrf_token(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract CSRF token from the page"""
        # Look for CSRF token in meta tag
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        if csrf_meta:
            return csrf_meta.get('content')
        
        # Look for CSRF token in hidden input
        csrf_input = soup.find('input', {'name': 'authenticity_token'})
        if csrf_input:
            return csrf_input.get('value')
        
        # Look for CSRF token in form
        csrf_form = soup.find('input', {'name': 'csrf_token'})
        if csrf_form:
            return csrf_form.get('value')
        
        return None
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling and retries"""
        kwargs.setdefault('timeout', config.request_timeout)
        
        for attempt in range(config.max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                self.last_activity = time.time()
                return response
            except requests.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == config.max_retries - 1:
                    raise RedmineScrapingError(f"Request failed after {config.max_retries} attempts: {e}")
                time.sleep(config.retry_delay * (attempt + 1))
        
        raise RedmineScrapingError("Unexpected error in request handling")
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login to Redmine using web scraping
        
        Args:
            username: Redmine username
            password: Redmine password
            
        Returns:
            Dict with login status and message
        """
        try:
            logger.info(f"Attempting to login to {config.login_url}")
            
            # Get login page to extract CSRF token
            response = self._make_request('GET', config.login_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract CSRF token
            csrf_token = self._get_csrf_token(soup)
            logger.debug(f"CSRF token: {csrf_token}")
            
            # Find login form
            login_form = soup.find('form', {'id': 'login-form'}) or soup.find('form', action=re.compile(r'login'))
            # Also check for form inside login div
            if not login_form:
                login_div = soup.find('div', {'id': 'login-form'})
                if login_div:
                    login_form = login_div.find('form')
            
            if not login_form:
                raise RedmineScrapingError("Login form not found on the page")
            
            # Prepare login data
            login_data = {
                'username': username,
                'password': password,
                'login': 'Login'  # Common submit button value
            }
            
            # Add CSRF token if found
            if csrf_token:
                login_data['authenticity_token'] = csrf_token
            
            # Find actual input field names from the form
            username_field = login_form.find('input', {'type': 'text'}) or login_form.find('input', {'name': re.compile(r'user|login|email')})
            password_field = login_form.find('input', {'type': 'password'})
            
            if username_field and username_field.get('name'):
                actual_username_field = username_field.get('name')
                login_data[actual_username_field] = username
                if actual_username_field != 'username':
                    del login_data['username']
            
            if password_field and password_field.get('name'):
                actual_password_field = password_field.get('name')
                login_data[actual_password_field] = password
                if actual_password_field != 'password':
                    del login_data['password']
            
            logger.debug(f"Prepared login data for Redmine login form (number of fields: {len(login_data)})")
            
            # Submit login form
            login_response = self._make_request('POST', config.login_url, data=login_data)
            
            # Check if login was successful
            # Usually, successful login redirects to home page or shows different content
            if login_response.url != config.login_url or 'login' not in login_response.url.lower():
                # If server redirected to a two-factor authentication confirmation page,
                # open it in the user's browser and let them complete the flow manually.
                if 'twofa' in login_response.url.lower() or '/account/twofa' in login_response.url.lower():
                    # Open the 2FA confirmation page in the user's browser and poll for
                    # authentication completion. This avoids blocking input() in non-interactive
                    # environments and centralizes the waiting logic here.
                    redirect_url = login_response.url
                    logger.info("Two-factor authentication required; opening browser for manual confirmation: %s", redirect_url)
                    try:
                        webbrowser.open(redirect_url)
                    except Exception:
                        logger.warning("Failed to open web browser for 2FA; please open %s manually", redirect_url)

                    # Poll projects page until authentication markers are present or timeout
                    max_wait = int(os.getenv('TWOFA_WAIT', '120'))
                    interval = int(os.getenv('TWOFA_POLL_INTERVAL', '5'))
                    waited = 0
                    logger.info("Waiting up to %s seconds for 2FA completion (poll interval %s)s", max_wait, interval)

                    while waited < max_wait:
                        try:
                            # Try accessing the projects page directly to check authentication
                            projects_resp = self._make_request('GET', config.projects_url)
                            soup = BeautifulSoup(projects_resp.text, 'html.parser')
                            
                            # Check if we get a proper projects page (not login page)
                            body = soup.find('body')
                            body_classes = body.get('class', []) if body else []
                            is_login_page = ('login' in projects_resp.url.lower() or 
                                           ('controller-account' in body_classes and 'action-login' in body_classes))
                            
                            if not is_login_page:
                                # Look for project content to confirm we're on the right page
                                project_table = soup.find('table', class_=re.compile(r'projects|list'))
                                project_links = soup.find_all('a', href=re.compile(r'/projects/[^/?]+'))
                                
                                if project_table or project_links:
                                    self.is_authenticated = True
                                    logger.info("Login successful after 2FA - projects page accessible")
                                    logger.debug(f"Session cookies after 2FA: {list(self.session.cookies.keys())}")
                                    return {
                                        'success': True,
                                        'message': 'Successfully logged in to Redmine (2FA completed)',
                                        'redirect_url': projects_resp.url
                                    }
                        except Exception as e:
                            logger.debug(f"Polling error while waiting for 2FA: {e}")

                        time.sleep(interval)
                        waited += interval

                    logger.warning("2FA was not completed within %s seconds", max_wait)
                    return {
                        'success': False,
                        'message': f'2FA not completed within {max_wait} seconds',
                        'redirect_url': redirect_url
                    }

                # Otherwise, check for user menu or logout link to confirm authentication
                soup = BeautifulSoup(login_response.text, 'html.parser')
                logout_link = soup.find('a', href=re.compile(r'logout'))
                user_menu = soup.find('div', {'id': 'account'}) or soup.find('div', class_=re.compile(r'user|account'))

                if logout_link or user_menu:
                    self.is_authenticated = True
                    logger.info("Login successful")
                    return {
                        'success': True,
                        'message': 'Successfully logged in to Redmine',
                        'redirect_url': login_response.url
                    }
            
            # Check for error messages
            soup = BeautifulSoup(login_response.text, 'html.parser')
            error_div = soup.find('div', {'id': 'flash_error'}) or soup.find('div', class_=re.compile(r'error|alert'))
            error_message = error_div.get_text(strip=True) if error_div else "Login failed - invalid credentials or form structure changed"
            
            logger.warning(f"Login failed: {error_message}")
            return {
                'success': False,
                'message': error_message
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
        if not self.is_authenticated:
            return {
                'success': False,
                'message': 'Not authenticated. Please login first.',
                'projects': []
            }
        
        try:
            logger.info(f"Fetching projects from {config.projects_url}")
            logger.debug(f"Current session cookies: {list(self.session.cookies.keys())}")
            logger.debug(f"Authentication status: {self.is_authenticated}")
            
            # If authenticated, first verify session by accessing home page
            if self.is_authenticated:
                logger.debug("Verifying session by accessing home page first")
                try:
                    home_response = self._make_request('GET', config.base_url)
                    home_soup = BeautifulSoup(home_response.text, 'html.parser')
                    
                    # Save home page for debugging
                    if config.debug:
                        with open('debug_home_page.html', 'w', encoding='utf-8') as f:
                            f.write(home_response.text)
                        logger.debug("Saved home page HTML to debug_home_page.html")
                    
                    # Check if still authenticated on home page
                    logout_link = home_soup.find('a', href=re.compile(r'logout'))
                    user_menu = home_soup.find('div', {'id': 'account'}) or home_soup.find('div', class_=re.compile(r'user|account'))
                    
                    logger.debug(f"Home page URL: {home_response.url}")
                    logger.debug(f"Logout link found: {logout_link is not None}")
                    logger.debug(f"User menu found: {user_menu is not None}")
                    
                    if not (logout_link or user_menu):
                        logger.warning("Session expired, authentication lost")
                        self.is_authenticated = False
                        return {
                            'success': False,
                            'message': 'Session expired. Please login again.',
                            'projects': []
                        }
                except Exception as e:
                    logger.warning(f"Error verifying session: {e}")
                    return {
                        'success': False,
                        'message': f'Error verifying session: {str(e)}',
                        'projects': []
                    }
            
            # Get projects page
            response = self._make_request('GET', config.projects_url)
            logger.debug(f"Response URL: {response.url}")
            logger.debug(f"Response status: {response.status_code}")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            projects = []
            
            # Debug: Log the page content structure
            page_title = soup.title.get_text() if soup.title else 'No title'
            logger.debug(f"Page title: {page_title}")
            
            # Save HTML response for debugging
            if config.debug:
                with open('debug_projects_page.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.debug("Saved projects page HTML to debug_projects_page.html")
            
            # Check if we're redirected to login page
            login_form = soup.find('form', {'id': 'login-form'}) or soup.find('form', action=re.compile(r'login'))
            login_div = soup.find('div', {'id': 'login-form'})
            body = soup.find('body')
            body_classes = body.get('class', []) if body else []
            is_login_page = ('login' in response.url.lower() or 
                           login_form or login_div or 
                           ('controller-account' in body_classes and 'action-login' in body_classes))
            
            if is_login_page:
                logger.debug(f"Detected login page. URL: {response.url}")
                logger.debug(f"Login form found: {login_form is not None}")
                logger.debug(f"Login div found: {login_div is not None}")
                logger.debug(f"Body classes: {body_classes}")
                
                return {
                    'success': False,
                    'message': f'Redirected to login page. Authentication required to view projects. Page title: {page_title}',
                    'projects': []
                }
            
            # Look for project list in different possible structures
            # Method 1: Table with project rows (most common in Redmine)
            project_table = soup.find('table', class_=re.compile(r'projects|list')) or soup.find('table', {'id': 'projects-index'})
            if project_table:
                logger.debug("Found project table")
                rows = project_table.find_all('tr')
                # Skip header row(s)
                data_rows = [row for row in rows if row.find('td')]
                
                for row in data_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 1:
                        # First cell usually contains project name and link
                        name_cell = cells[0]
                        project_link = name_cell.find('a')
                        if project_link and project_link.get('href'):
                            project_name = project_link.get_text(strip=True)
                            project_url = urljoin(config.base_url, project_link.get('href', ''))
                            
                            # Extract project ID from URL
                            project_id = None
                            url_match = re.search(r'/projects/([^/?]+)', project_link.get('href', ''))
                            if url_match:
                                project_id = url_match.group(1)
                            
                            # Get description if available (usually in second column)
                            description = ''
                            if len(cells) > 1:
                                desc_cell = cells[1]
                                description = desc_cell.get_text(strip=True)
                            
                            if project_name and project_id:  # Only add if we have valid data
                                projects.append({
                                    'id': project_id,
                                    'name': project_name,
                                    'description': description,
                                    'url': project_url
                                })
            
            # Method 2: List items or div containers
            if not projects:
                logger.debug("No table found, looking for list items or divs")
                # Look for list items
                project_items = soup.find_all('li', class_=re.compile(r'project')) or soup.find_all('div', class_=re.compile(r'project'))
                for item in project_items:
                    project_link = item.find('a', href=re.compile(r'/projects/[^/?]+'))
                    if project_link:
                        project_name = project_link.get_text(strip=True)
                        project_url = urljoin(config.base_url, project_link.get('href', ''))
                        
                        # Extract project ID from URL
                        project_id = None
                        url_match = re.search(r'/projects/([^/?]+)', project_link.get('href', ''))
                        if url_match:
                            project_id = url_match.group(1)
                        
                        if project_name and project_id:
                            projects.append({
                                'id': project_id,
                                'name': project_name,
                                'description': '',
                                'url': project_url
                            })
            
            # Method 3: General project links (fallback)
            if not projects:
                logger.debug("No structured list found, looking for any project links")
                project_links = soup.find_all('a', href=re.compile(r'/projects/[^/?]+/?$'))
                for link in project_links:
                    project_name = link.get_text(strip=True)
                    # Filter out navigation links and empty names
                    if (project_name and 
                        len(project_name) > 1 and
                        not project_name.lower() in ['projects', 'new project', 'settings', 'administration', 'home']):
                        
                        project_url = urljoin(config.base_url, link.get('href', ''))
                        
                        # Extract project ID from URL
                        project_id = None
                        url_match = re.search(r'/projects/([^/?]+)', link.get('href', ''))
                        if url_match:
                            project_id = url_match.group(1)
                        
                        if project_id:
                            projects.append({
                                'id': project_id,
                                'name': project_name,
                                'description': '',
                                'url': project_url
                            })
            
            # Remove duplicates based on project ID
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
                # If no projects found, provide more detailed debugging info
                page_text = soup.get_text()[:500]  # First 500 chars for debugging
                return {
                    'success': False,
                    'message': f'No projects found on the page. Page might require authentication or have different structure. Page preview: {page_text}...',
                    'projects': []
                }
            
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            return {
                'success': False,
                'message': f"Error fetching projects: {str(e)}",
                'projects': []
            }
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout from Redmine
        
        Returns:
            Dict with logout status
        """
        try:
            if self.is_authenticated:
                logger.info("Logging out from Redmine")
                response = self._make_request('GET', config.logout_url)
                
            self.is_authenticated = False
            self.session.cookies.clear()
            
            return {
                'success': True,
                'message': 'Successfully logged out from Redmine'
            }
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            self.is_authenticated = False
            self.session.cookies.clear()
            return {
                'success': True,  # Still consider it successful since we cleared the session
                'message': f'Logged out (with warning: {str(e)})'
            }
    
    def is_session_valid(self) -> bool:
        """Check if the current session is still valid"""
        if not self.is_authenticated:
            return False
        
        if self.last_activity and (time.time() - self.last_activity) > config.session_timeout:
            logger.info("Session expired due to timeout")
            self.is_authenticated = False
            return False
        
        return True