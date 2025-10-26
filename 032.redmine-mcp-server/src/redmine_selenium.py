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
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass