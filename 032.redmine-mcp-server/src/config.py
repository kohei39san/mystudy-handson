"""
Redmine MCP Server Configuration
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RedmineConfig:
    """Redmine server configuration"""
    
    def __init__(self):
        # Redmine server URL (can be overridden by environment variable)
        self.base_url: str = os.getenv('REDMINE_URL', 'http://localhost:3000')
        
        # Remove trailing slash if present
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
        
        # Login and logout URLs
        self.login_url: str = f"{self.base_url}/login"
        self.logout_url: str = f"{self.base_url}/logout"
        self.projects_url: str = f"{self.base_url}/projects"
        
        # Session timeout (in seconds)
        self.session_timeout: int = int(os.getenv('SESSION_TIMEOUT', '3600'))
        
        # Request timeout (in seconds)
        self.request_timeout: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
        # User agent for requests
        self.user_agent: str = os.getenv('USER_AGENT', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Default headers for requests
        self.default_headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Retry configuration
        self.max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay: float = float(os.getenv('RETRY_DELAY', '1.0'))
        
        # Debug mode
        self.debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'

# Global configuration instance
config = RedmineConfig()