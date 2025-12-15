#!/usr/bin/env python3
"""
Redmine MCP Server
A Model Context Protocol server for interacting with Redmine via web scraping
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    ServerCapabilities
)

# Import Pydantic schemas from separate module
from schemas import (
    LoginRequest,
    EmptyRequest,
    SearchIssuesRequest,
    CreateIssueRequest,
    UpdateIssueRequest,
    IssueIdRequest,
    ProjectIdRequest,
    TrackerFieldsRequest,
    TimeEntriesRequest,
    CreationStatusesRequest,
    AvailableStatusesRequest,
    OptionalProjectIdRequest
)

# Import our modules with proper error handling
try:
    from redmine_selenium import RedmineSeleniumScraper
    from config import config
except ImportError:
    # Try relative imports if absolute imports fail
    try:
        from .redmine_selenium import RedmineSeleniumScraper
        from .config import config
    except ImportError as e:
        print(f"Failed to import required modules: {e}")
        print("Please ensure you're running from the correct directory and all dependencies are installed.")
        sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO if config.debug else logging.WARNING)
logger = logging.getLogger(__name__)

class RedmineMCPServer:
    """Redmine MCP Server implementation"""
    
    def __init__(self):
        self.server = Server("redmine-mcp-server")
        self.scraper = RedmineSeleniumScraper()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="redmine_login",
                    description="Login to Redmine using username and password",
                    inputSchema=LoginRequest.model_json_schema()
                ),
                Tool(
                    name="get_projects",
                    description="Get list of projects from Redmine (requires authentication)",
                    inputSchema=EmptyRequest.model_json_schema()
                ),
                Tool(
                    name="logout",
                    description="Logout from Redmine and clear session",
                    inputSchema=EmptyRequest.model_json_schema()
                ),
                Tool(
                    name="get_server_info",
                    description="Get information about the Redmine server configuration",
                    inputSchema=EmptyRequest.model_json_schema()
                ),
                Tool(
                    name="search_issues",
                    description="Search for issues in Redmine with various filters",
                    inputSchema=SearchIssuesRequest.model_json_schema()
                ),
                Tool(
                    name="get_issue_details",
                    description="Get detailed information about a specific issue",
                    inputSchema=IssueIdRequest.model_json_schema()
                ),
                Tool(
                    name="get_available_trackers",
                    description="Get available tracker options from issue creation page",
                    inputSchema=OptionalProjectIdRequest.model_json_schema()
                ),
                Tool(
                    name="get_creation_statuses",
                    description="Get available status options from new issue creation page for a specific tracker",
                    inputSchema=CreationStatusesRequest.model_json_schema()
                ),
                Tool(
                    name="get_available_statuses",
                    description="Get available status options for a specific issue",
                    inputSchema=AvailableStatusesRequest.model_json_schema()
                ),
                Tool(
                    name="create_issue",
                    description="Create a new issue in Redmine",
                    inputSchema=CreateIssueRequest.model_json_schema()
                ),
                Tool(
                    name="get_tracker_fields",
                    description="Get available fields for a specific tracker from new issue page",
                    inputSchema=TrackerFieldsRequest.model_json_schema()
                ),
                Tool(
                    name="update_issue",
                    description="Update an issue with new field values",
                    inputSchema=UpdateIssueRequest.model_json_schema()
                ),
                Tool(
                    name="get_project_members",
                    description="Get project members from project settings page",
                    inputSchema=ProjectIdRequest.model_json_schema()
                ),
                Tool(
                    name="get_time_entries",
                    description="Get time entries (作業時間) for a project with optional filters",
                    inputSchema=TimeEntriesRequest.model_json_schema()
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "redmine_login":
                    return await self._handle_login(arguments)
                elif name == "get_projects":
                    return await self._handle_get_projects(arguments)
                elif name == "logout":
                    return await self._handle_logout(arguments)
                elif name == "get_server_info":
                    return await self._handle_get_server_info(arguments)
                elif name == "search_issues":
                    return await self._handle_search_issues(arguments)
                elif name == "get_issue_details":
                    return await self._handle_get_issue_details(arguments)
                elif name == "get_available_trackers":
                    return await self._handle_get_available_trackers(arguments)
                elif name == "get_creation_statuses":
                    return await self._handle_get_creation_statuses(arguments)
                elif name == "get_available_statuses":
                    return await self._handle_get_available_statuses(arguments)
                elif name == "get_tracker_fields":
                    return await self._handle_get_tracker_fields(arguments)
                elif name == "create_issue":
                    return await self._handle_create_issue(arguments)
                elif name == "update_issue":
                    return await self._handle_update_issue(arguments)
                elif name == "get_project_members":
                    return await self._handle_get_project_members(arguments)
                elif name == "get_time_entries":
                    return await self._handle_get_time_entries(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    async def _handle_login(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle login tool call"""
        username = arguments.get("username")
        password = arguments.get("password")
        
        if not username or not password:
            return [TextContent(
                type="text",
                text="Error: Both username and password are required"
            )]
        
        logger.info(f"Login attempt for user: {username}")
        result = self.scraper.login(username, password)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_get_projects(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get projects tool call"""
        logger.info("Fetching projects list")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_projects()
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_logout(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle logout tool call"""
        logger.info("Logout requested")
        result = self.scraper.logout()
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_get_server_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get server info tool call"""
        info = {
            "server_url": config.base_url,
            "login_url": config.login_url,
            "projects_url": config.projects_url,
            "session_timeout": config.session_timeout,
            "request_timeout": config.request_timeout,
            "authenticated": self.scraper.is_authenticated,
            "session_valid": self.scraper.is_authenticated
        }
        
        response_text = "**Redmine Server Information:**\n"
        response_text += "=" * 40 + "\n"
        response_text += f"Server URL: {info['server_url']}\n"
        response_text += f"Login URL: {info['login_url']}\n"
        response_text += f"Projects URL: {info['projects_url']}\n"
        response_text += f"Session Timeout: {info['session_timeout']} seconds\n"
        response_text += f"Request Timeout: {info['request_timeout']} seconds\n"
        response_text += f"Authentication Status: {'[AUTH] Authenticated' if info['authenticated'] else '[NO-AUTH] Not Authenticated'}\n"
        response_text += f"Session Valid: {'[VALID] Valid' if info['session_valid'] else '[INVALID] Invalid/Expired'}\n"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
    
    async def _handle_search_issues(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search issues tool call"""
        logger.info("Searching for issues")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        # Pass all arguments directly to scraper
        search_params = {k: v for k, v in arguments.items() if v is not None}
        
        result = self.scraper.search_issues(**search_params)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_get_issue_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get issue details tool call"""
        issue_id = arguments.get("issue_id")
        
        if not issue_id:
            return [TextContent(
                type="text",
                text="[ERROR] Issue ID is required"
            )]
        
        logger.info(f"Fetching details for issue #{issue_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_issue_details(issue_id)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_get_available_trackers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get available trackers tool call"""
        project_id = arguments.get("project_id")
        
        logger.info(f"Getting available trackers for project: {project_id or 'all'}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_available_trackers(project_id)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_get_creation_statuses(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get creation statuses tool call"""
        project_id = arguments.get("project_id")
        tracker_id = arguments.get("tracker_id")
        
        if not project_id or not tracker_id:
            return [TextContent(
                type="text",
                text="[ERROR] Both project ID and tracker ID are required"
            )]
        
        logger.info(f"Getting creation statuses for project {project_id}, tracker {tracker_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_creation_statuses(project_id, tracker_id)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_get_available_statuses(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get available statuses tool call"""
        issue_id = arguments.get("issue_id")
        
        if not issue_id:
            return [TextContent(
                type="text",
                text="[ERROR] Issue ID is required"
            )]
        
        logger.info(f"Getting available statuses for issue #{issue_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_available_statuses(issue_id)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_get_tracker_fields(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get tracker fields tool call"""
        project_id = arguments.get("project_id")
        issue_tracker_id = arguments.get("issue_tracker_id")
        
        if not project_id:
            return [TextContent(
                type="text",
                text="[ERROR] Project ID is required"
            )]
        
        if not issue_tracker_id:
            return [TextContent(
                type="text",
                text="[ERROR] Tracker ID is required"
            )]
        
        logger.info(f"Getting tracker fields for project {project_id}, tracker {issue_tracker_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_tracker_fields(project_id, issue_tracker_id)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_create_issue(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle create issue tool call"""
        project_id = arguments.get("project_id")
        subject = arguments.get("issue_subject") or arguments.get("subject")
        
        if not project_id or not subject:
            return [TextContent(
                type="text",
                text="[ERROR] Project ID and subject are required"
            )]
        
        logger.info(f"Creating issue in project {project_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        # Extract parameters from arguments
        issue_tracker_id = arguments.get('issue_tracker_id')
        issue_subject = arguments.get('issue_subject') or subject  # fallback to subject for compatibility
        
        if not issue_tracker_id:
            return [TextContent(
                type="text",
                text="[ERROR] Tracker ID is required"
            )]
        
        # Build create_params
        create_params = {}
        
        # Add fields from fields object first
        if arguments.get('fields'):
            create_params.update(arguments['fields'])
        
        # Set issue_subject (use subject from fields if available, otherwise use issue_subject parameter)
        if 'subject' in create_params:
            create_params['issue_subject'] = create_params.pop('subject')
        else:
            create_params['issue_subject'] = issue_subject
        

        
        result = self.scraper.create_issue(project_id, str(issue_tracker_id), **create_params)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_update_issue(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle update issue tool call"""
        issue_id = arguments.get("issue_id")
        
        if not issue_id:
            return [TextContent(
                type="text",
                text="[ERROR] Issue ID is required"
            )]
        
        logger.info(f"Updating issue #{issue_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        # Get fields to update
        update_params = arguments.get('fields', {})
        
        if not update_params:
            return [TextContent(
                type="text",
                text="[ERROR] Fields object with at least one field to update must be provided"
            )]
        
        result = self.scraper.update_issue(issue_id, **update_params)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_get_project_members(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get project members tool call"""
        project_id = arguments.get("project_id")
        
        if not project_id:
            return [TextContent(
                type="text",
                text="[ERROR] Project ID is required"
            )]
        
        logger.info(f"Getting project members for project: {project_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_project_members(project_id)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]
    
    async def _handle_get_time_entries(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get time entries tool call"""
        project_id = arguments.get("project_id")
        
        if not project_id:
            return [TextContent(
                type="text",
                text="[ERROR] Project ID is required"
            )]
        
        logger.info(f"Getting time entries for project: {project_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        # Extract parameters from arguments
        filter_params = {k: v for k, v in arguments.items() if v is not None and k != 'project_id'}
        
        result = self.scraper.get_time_entries(project_id, **filter_params)
        
        return [TextContent(
            type="text",
            text=str(result)
        )]

    async def run(self):
        """Run the MCP server"""
        logger.info(f"Starting Redmine MCP Server for {config.base_url}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="redmine-mcp-server",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        tools={}
                    )
                )
            )

async def main():
    """Main entry point"""
    server = RedmineMCPServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)