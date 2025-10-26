"""
Redmine Web Scraper
Handles authentication and data extraction from Redmine via web scraping
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import time
import logging
from urllib.parse import urljoin, urlparse
import re
import os
import sys

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
            
            logger.debug(f"Login data keys: {list(login_data.keys())}")
            
            # Submit login form
            login_response = self._make_request('POST', config.login_url, data=login_data)
            
            # Check if login was successful
            # Usually, successful login redirects to home page or shows different content
            if login_response.url != config.login_url or 'login' not in login_response.url.lower():
                # Check for user menu or logout link to confirm authentication
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
            
            # Get projects page
            response = self._make_request('GET', config.projects_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            projects = []
            
            # Look for project list in different possible structures
            # Method 1: Table with project rows
            project_table = soup.find('table', class_=re.compile(r'projects|list'))
            if project_table:
                rows = project_table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        name_cell = cells[0]
                        project_link = name_cell.find('a')
                        if project_link:
                            project_name = project_link.get_text(strip=True)
                            project_url = urljoin(config.base_url, project_link.get('href', ''))
                            
                            # Extract project ID from URL
                            project_id = None
                            url_match = re.search(r'/projects/([^/]+)', project_link.get('href', ''))
                            if url_match:
                                project_id = url_match.group(1)
                            
                            # Get description if available
                            description = ''
                            if len(cells) > 1:
                                desc_cell = cells[1]
                                description = desc_cell.get_text(strip=True)
                            
                            projects.append({
                                'id': project_id,
                                'name': project_name,
                                'description': description,
                                'url': project_url
                            })
            
            # Method 2: List of project links
            if not projects:
                project_links = soup.find_all('a', href=re.compile(r'/projects/[^/]+/?$'))
                for link in project_links:
                    project_name = link.get_text(strip=True)
                    if project_name and not project_name.lower() in ['projects', 'new project', 'settings']:
                        project_url = urljoin(config.base_url, link.get('href', ''))
                        
                        # Extract project ID from URL
                        project_id = None
                        url_match = re.search(r'/projects/([^/]+)', link.get('href', ''))
                        if url_match:
                            project_id = url_match.group(1)
                        
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
            return {
                'success': True,
                'message': f'Successfully retrieved {len(unique_projects)} projects',
                'projects': unique_projects
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